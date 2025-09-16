"""
Intelligent Playwright wrapper with LLM-powered selector improvement.

This module provides a drop-in replacement for Playwright page objects that automatically
attempts to improve failing selectors using LLM when the original selector fails.

Usage:
    from skyramp.smart_playwright import wrap_playwright_page
    
    # Wrap your existing Playwright page
    smart_page = wrap_playwright_page(page)
    
    # Use it exactly like a normal Playwright page
    smart_page.get_by_role("button", name="Submit").click()
    # If the selector fails, it will automatically try LLM-improved alternatives
"""

import ctypes
import json
import logging
import os
from typing import Optional, Dict, Any, List

from skyramp.utils import _library

logger = logging.getLogger(__name__)


def debug(args):
    """ helper function to print log messages per env var"""
    if os.environ.get('SKYRAMP_DEBUG', 'false') == 'true':
        print(args)


class SelectorCache:
    """Simple in-memory cache for successful selector improvements."""

    def __init__(self):
        self._cache: Dict[str, List[Dict[str, Any]]] = {}

    def get(self, original_selector: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached suggestions for a selector."""
        return self._cache.get(original_selector)

    def put(self, original_selector: str, suggestions: List[Dict[str, Any]]) -> None:
        """Cache suggestions for a selector."""
        self._cache[original_selector] = suggestions

    def clear(self) -> None:
        """Clear all cached suggestions."""
        self._cache.clear()


# Global cache instance
_selector_cache = SelectorCache()


# pylint: disable=too-many-locals
def improve_selector_with_llm(
    original_selector: str,
    error_message: str,
    dom_context: str = "",
    page_title: str = "",
    page_url: str = ""
) -> Optional[List[Dict[str, Any]]]:
    """
    Call the Go library to improve a failing Playwright selector using LLM.
    
    Args:
        original_selector: The failing selector
        error_message: The error message from Playwright
        dom_context: Relevant DOM context
        page_title: Page title for context
        page_url: Page URL for context
    
    Returns:
        List of selector suggestions or None if failed
    """
    # Check cache first
    cached_suggestions = _selector_cache.get(original_selector)
    if cached_suggestions:
        logger.info("Using cached suggestions for selector: %s", original_selector)
        return cached_suggestions

    try:
        request_data = {
            "original_selector": original_selector,
            "error_message": error_message,
            "dom_context": dom_context,
            "page_title": page_title,
            "page_url": page_url
        }

        request_json = json.dumps(request_data).encode('utf-8')

        func = _library.improvePlywrightSelectorWrapper

        class ResponseWrapper(ctypes.Structure):
            """The response structure matching Go's C.struct_response_wrapper"""
            _fields_ = [
                ("response", ctypes.c_char_p),
                ("error", ctypes.c_char_p),
            ]

        func.argtypes = [ctypes.c_char_p]
        func.restype = ResponseWrapper

        response_wrapper = func(request_json)

        if response_wrapper.error:
            #pylint: disable=no-member  # check this later
            error_msg = ctypes.c_char_p(response_wrapper.error).value.decode('utf-8')
            logger.error("LLM selector improvement failed: %s", error_msg)
            return None

        if response_wrapper.response:
            #pylint: disable=no-member  # check this later
            response_json = ctypes.c_char_p(response_wrapper.response).value.decode('utf-8')
            response_data = json.loads(response_json)

            suggestions = response_data.get("suggestions", [])
            if suggestions:
                # Cache successful suggestions
                _selector_cache.put(original_selector, suggestions)
                logger.info("Got %d selector suggestions from LLM", len(suggestions))
                return suggestions

        return None
    #pylint: disable=broad-exception-caught
    except Exception as e:
        logger.error("Failed to call LLM for selector improvement: %s", e)
        return None


class SkyrampPlaywrightLocator:
    """
    Intelligent wrapper for Playwright Locator with LLM-powered selector improvement.
    """

    def __init__(self, skyramp_page, locator, prev_locator, selector_info=None, hydration=False):
        self._skyramp_page = skyramp_page
        self._locator = locator
        self._previous_locator = prev_locator
        self._selector_info = selector_info or {}
        self._hydration = hydration
        self._current_selector = self._build_selector_string()

        # for future use
        self._fname = None
        self._exec_param = None
        self._exec_args = None
        self._locator_count = 0

    #pylint: disable=too-many-return-statements
    def _build_selector_string(self):
        """Build a readable selector string from selector info for LLM context."""
        if not self._selector_info:
            return str(self._locator) if hasattr(self._locator, '__str__') else ""

        method = self._selector_info.get('method', 'locator')
        args = self._selector_info.get('args', [])
        kwargs = self._selector_info.get('kwargs', {})

        # Build a Playwright-style selector string
        if method == 'get_by_role':
            role = args[0] if args else 'unknown'
            name = kwargs.get('name', '')
            if name:
                return f"page.get_by_role('{role}', name='{name}')"

            return f"page.get_by_role('{role}')"
        if method == 'get_by_text':
            text = args[0] if args else 'unknown'
            return f"page.get_by_text('{text}')"
        if method == 'get_by_label':
            label = args[0] if args else 'unknown'
            return f"page.get_by_label('{label}')"
        if method == 'get_by_test_id':
            test_id = args[0] if args else 'unknown'
            return f"page.get_by_test_id('{test_id}')"
        if method == 'locator':
            selector = args[0] if args else 'unknown'
            return f"page.locator('{selector}')"

        return f"page.{method}({', '.join(str(arg) for arg in args)})"

    @property
    def hydration(self):
        """ return locator's hydration flag """
        return self._hydration

    def _is_prev_hydration(self):
        """ check if previous locator has hydration flag set """
        return self._previous_locator is not None and self._previous_locator.hydration

    @property
    def locator_count(self):
        """return current locator's count in the page"""
        return self._locator_count

    @property
    def current_selector(self):
        """ return current selector in string """
        return self._current_selector

    def _should_attempt_improvement(self, error_message: str, error_type=None) -> bool:
        """Determine if an error is worth trying LLM improvement."""
        improvement_keywords = [
            "timeout",
            "not found",
            "no element",
            "not visible",
            "not attached",
            "selector resolved to hidden",
            "element is not enabled",
        ]

        # Check for specific Playwright error types
        if error_type:
            playwright_error_types = [
                "TimeoutError",
                "Error",
                "LocatorAssertionError"
            ]
            if any(error_type.__name__.endswith(err_type) for err_type in playwright_error_types):
                return True

        error_lower = error_message.lower()
        return any(keyword in error_lower for keyword in improvement_keywords)

    def _is_selector_method(self, method_name: str) -> bool:
        """Check if a method uses selectors that can be improved."""
        selector_methods = [
            'click', 'fill', 'type', 'press', 'check', 'uncheck', 'select_option',
            'hover', 'focus', 'blur', 'scroll_into_view_if_needed', 'screenshot',
            'text_content', 'inner_text', 'inner_html', 'get_attribute', 'is_visible',
            'is_enabled', 'is_checked', 'is_disabled', 'is_editable', 'is_hidden'
        ]
        return method_name in selector_methods

    def _test_locator_exists(self, locator):
        """Test if a locator can find an element without performing actions."""
        try:
            # Use count() to check existence without throwing an error
            # This doesn't perform any actions, just checks if element exists
            count = locator.count()
            return count > 0
        #pylint: disable=broad-exception-caught
        except Exception:
            return False

    def execute(self):
        """execute actions associated with the locator"""
        debug(f'execute { self._fname} from { self._current_selector } ' +
              f'with { self._exec_param } {self._exec_args}')
        f = getattr(self._locator, self._fname)
        if self._exec_param is None:
            return f(**self._exec_args)

        return f(self._exec_param, **self._exec_args)

    # pylint: disable=too-many-return-statements,too-many-branches
    def _smart_retry_with_fallback(self, fname, param, **kwargs):
        self._fname = fname
        self._exec_param = param
        self._exec_args = kwargs

        locator_count = None
        try:
            locator_count = self._locator.count()
        #pylint: disable=broad-exception-caught
        except Exception:
            # locator does not exist
            locator_count = None

        self._locator_count = locator_count
        # pylint: disable=line-too-long
        hydration_message = "Potential hydration. Please add enough wait_for_timeout() or use hydration flag"

        if locator_count == 1:
            try:
                return self.execute()
            #pylint: disable=broad-exception-caught
            except Exception as e:
                debug(f'case 1 { str(e) }')
                error_message = str(e)
                if "TimeoutError" in error_message:
                    try:
                        return self.execute()
                    #pylint: disable=broad-exception-caught
                    except Exception as new_e:
                        raise Exception(hydration_message) from new_e
        elif locator_count > 0:
            # this need to be implemented
            return self.execute()
        else:
            try:
                if self._previous_locator is not None and (self._is_prev_hydration()
                                                           or self._previous_locator.locator_count == 0):
                    debug(f'previous action { self._previous_locator.current_selector } is potentially associated with hydration { self._is_prev_hydration()}')
                    # wait for a short time to finish hydration
                    self._skyramp_page.page.wait_for_timeout(1500)
                    # then re-execute the previous locator
                    self._previous_locator.execute()

                # then execute the current one
                return self.execute()
            #pylint: disable=broad-exception-caught
            except Exception as e:
                debug(f'case 2 { str(e) }')
                error_message = str(e)
                if "TimeoutError" in error_message:
                    try :
                        return self.execute()
                    #pylint: disable=broad-exception-caught
                    except Exception as new_e:
                        raise Exception(hydration_message) from new_e
                else:
                    raise e
        return self.execute()

    def click(self, **kwargs):
        """Wrap click"""
        return self._smart_retry_with_fallback("click", None, **kwargs)

    def fill(self, text, **kwargs):
        """Wrap fill"""
        return self._smart_retry_with_fallback("fill", text, **kwargs)

    def type(self, text, **kwargs):
        """Wrap type"""
        return self._smart_retry_with_fallback("type", text, **kwargs)

    def press(self, key, **kwargs):
        """Wrap press"""
        return self._smart_retry_with_fallback("press", key, **kwargs)

    def check(self, **kwargs):
        """Wrap check"""
        return self._smart_retry_with_fallback("check", None, **kwargs)

    def uncheck(self, **kwargs):
        """Wrap uncheck"""
        return self._smart_retry_with_fallback("uncheck", None, **kwargs)

    def select_option(self, value=None, **kwargs):
        """Wrap select_option"""
        return self._smart_retry_with_fallback("select_option", value, **kwargs)

    def hover(self, **kwargs):
        """Wrap hover"""
        return self._smart_retry_with_fallback("hover", None, **kwargs)

    def text_content(self, **kwargs):
        """Wrap text_content"""
        return self._smart_retry_with_fallback("text_content", None, **kwargs)

    def is_visible(self, **kwargs):
        """Wrap is_visible"""
        return self._smart_retry_with_fallback("is_visible", None, **kwargs)

    def nth(self, index):
        """Wrap nth and return a new locator"""
        new_locator = self._locator.nth(index)
        new_selector_info = self._selector_info.copy() if self._selector_info else {}
        if 'method' in new_selector_info and new_selector_info['method'] == 'locator':
            original_selector = new_selector_info.get('args', [''])[0]
            new_selector_info['args'] = [f"{original_selector}.nth({index})"]

        return self._skyramp_page.new_skyramp_playwright_locator(new_locator, new_selector_info)

    def first(self):
        """Wrap first and return a new locator"""
        new_locator = self._locator.first()
        new_selector_info = self._selector_info.copy() if self._selector_info else {}
        if 'method' in new_selector_info and new_selector_info['method'] == 'locator':
            original_selector = new_selector_info.get('args', [''])[0]
            new_selector_info['args'] = [f"{original_selector}.first()"]

        return self._skyramp_page.new_skyramp_playwright_locator(new_locator, new_selector_info)

    def last(self):
        """Wrap first and return a new locator"""
        new_locator = self._locator.last()
        new_selector_info = self._selector_info.copy() if self._selector_info else {}
        if 'method' in new_selector_info and new_selector_info['method'] == 'locator':
            original_selector = new_selector_info.get('args', [''])[0]
            new_selector_info['args'] = [f"{original_selector}.last()"]

        return self._skyramp_page.new_skyramp_playwright_locator(new_locator, new_selector_info)

    @property
    def locator(self):
        """Get the underlying Playwright locator for assertions and other uses."""
        return self._locator

    def __getattr__(self, name):
        """Forward other method calls to the original locator."""
        return getattr(self._locator, name)


class SkyrampPlaywrightPage:
    """
    Intelligent wrapper for Playwright Page with LLM-powered selector improvement.
    """
    def __init__(self, page):
        self._page = page
        self._locators = []

    @property
    def page(self):
        """ return original playwright page """
        return self._page

    def _push_locator(self, locator):
        self._locators.append(locator)

    def _get_last_locator(self):
        if len(self._locators) == 0:
            return None

        return self._locators[-1]

    def new_skyramp_playwright_locator(self, original_locator, selector_info, hydration=False):
        """ create a skyramp locator that wraps playwright locator """
        prev_locator = self._get_last_locator()
        new_locator = SkyrampPlaywrightLocator(self, original_locator,
                                               prev_locator, selector_info, hydration)
        self._push_locator(new_locator)
        return new_locator

    def locator(self, selector: str, **kwargs) -> SkyrampPlaywrightLocator:
        """Create a smart locator with LLM fallback."""
        hydration=False
        if "hydration" in kwargs:
            hydration = kwargs["hydration"]
            del kwargs["hydration"]

        original_locator = self._page.locator(selector, **kwargs)
        selector_info = {
            'method': 'locator',
            'args': [selector],
            'kwargs': kwargs
        }
        return self.new_skyramp_playwright_locator(original_locator, selector_info, hydration)

    def get_by_role(self, role: str, **kwargs) -> SkyrampPlaywrightLocator:
        """Create a smart locator by role with LLM fallback."""
        hydration=False
        if "hydration" in kwargs:
            hydration = kwargs["hydration"]
            del kwargs["hydration"]


        original_locator = self._page.get_by_role(role, **kwargs)
        selector_info = {
            'method': 'get_by_role',
            'args': [role],
            'kwargs': kwargs
        }
        return self.new_skyramp_playwright_locator(original_locator, selector_info, hydration)

    def get_by_text(self, text: str, **kwargs) -> SkyrampPlaywrightLocator:
        """Create a smart locator by text with LLM fallback."""
        hydration=False
        if "hydration" in kwargs:
            hydration = kwargs["hydration"]
            del kwargs["hydration"]

        original_locator = self._page.get_by_text(text, **kwargs)
        selector_info = {
            'method': 'get_by_text',
            'args': [text],
            'kwargs': kwargs
        }
        return self.new_skyramp_playwright_locator(original_locator, selector_info, hydration)

    def get_by_label(self, label: str, **kwargs) -> SkyrampPlaywrightLocator:
        """Create a smart locator by label with LLM fallback."""
        hydration=False
        if "hydration" in kwargs:
            hydration = kwargs["hydration"]
            del kwargs["hydration"]
        original_locator = self._page.get_by_label(label, **kwargs)
        selector_info = {
            'method': 'get_by_label',
            'args': [label],
            'kwargs': kwargs
        }
        return self.new_skyramp_playwright_locator(original_locator, selector_info, hydration)

    def get_by_test_id(self, test_id: str, **kwargs) -> SkyrampPlaywrightLocator:
        """Create a smart locator by test ID with LLM fallback."""
        hydration=False
        if "hydration" in kwargs:
            hydration = kwargs["hydration"]
            del kwargs["hydration"]
        original_locator = self._page.get_by_test_id(test_id)
        selector_info = {
            'method': 'get_by_test_id',
            'args': [test_id],
            'kwargs': {}
        }
        return self.new_skyramp_playwright_locator(original_locator, selector_info, hydration)

    def get_by_title(self, title: str, **kwargs) -> SkyrampPlaywrightLocator:
        """Create a smart locator by title with LLM fallback."""
        hydration=False
        if "hydration" in kwargs:
            hydration = kwargs["hydration"]
            del kwargs["hydration"]
        original_locator = self._page.get_by_title(title, **kwargs)
        selector_info = {
            'method': 'get_by_title',
            'args': [title],
            'kwargs': kwargs
        }
        return self.new_skyramp_playwright_locator(original_locator, selector_info, hydration)

    def get_by_placeholder(self, placeholder: str, **kwargs) -> SkyrampPlaywrightLocator:
        """Create a smart locator by placeholder with LLM fallback."""
        hydration=False
        if "hydration" in kwargs:
            hydration = kwargs["hydration"]
            del kwargs["hydration"]
        original_locator = self._page.get_by_placeholder(placeholder, **kwargs)
        selector_info = {
            'method': 'get_by_placeholder',
            'args': [placeholder],
            'kwargs': kwargs
        }
        return self.new_skyramp_playwright_locator(original_locator, selector_info, hydration)

    def get_by_alt_text(self, alt: str, **kwargs) -> SkyrampPlaywrightLocator:
        """Create a smart locator by alt text with LLM fallback."""
        hydration=False
        if "hydration" in kwargs:
            hydration = kwargs["hydration"]
            del kwargs["hydration"]
        original_locator = self._page.get_by_alt_text(alt, **kwargs)
        selector_info = {
            'method': 'get_by_alt_text',
            'args': [alt],
            'kwargs': kwargs
        }
        return self.new_skyramp_playwright_locator(original_locator, selector_info, hydration)

    def clear_selector_cache(self):
        """Clear the cached selector improvements."""
        _selector_cache.clear()

    def __getattr__(self, name):
        """Forward other method calls to the original page."""
        return getattr(self._page, name)


# Convenience function for easy integration
def new_skyramp_playwright_page(page) -> SkyrampPlaywrightPage:
    """
    Wrap a Playwright page with intelligent selector improvement.
    
    Args:
        page: Original Playwright page object
    
    Returns:
        SkyrampPlaywrightPage with LLM-powered selector improvement
        
    Example:
        from playwright.sync_api import sync_playwright
        from skyramp.smart_playwright import wrap_playwright_page
        
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            
            # Wrap the page for intelligent selector improvement
            smart_page = wrap_playwright_page(page)
            
            # Use it like a normal page - fallback to LLM if selectors fail
            smart_page.goto("https://example.com")
            smart_page.get_by_role("button", name="Submit").click()
    """
    logger.info("🧠 ENTRY POINT: Wrapping Playwright page with SkyrampPlaywrightPage" +
                "for LLM-powered selector improvement")
    return SkyrampPlaywrightPage(page)
