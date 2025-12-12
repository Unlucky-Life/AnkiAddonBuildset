"""JavaScript injection utilities for web player control and ad blocking.

This module provides all JavaScript code used to interact with and control the
embedded web player. It handles:
    - Ad blocking via CSS injection and DOM manipulation
    - Playback control via button clicks and keyboard events
    - Dynamic ad removal using MutationObserver

The JavaScript code is organized into a class with static methods, each returning
a complete, self-contained JavaScript snippet that can be executed in the web view.

Architecture:
    - Early injection (DocumentCreation): CSS-based ad hiding
    - Post-load injection: Comprehensive ad removal and monitoring
    - Control scripts: Button finding and keyboard event dispatch

All JavaScript is designed to work with YouTube Music and YouTube's current
(as of 2025) DOM structure, though it includes fallbacks for robustness.

Typical usage example:
    >>> from utils.javascript import JavaScriptInjector
    >>> script = JavaScriptInjector.get_play_pause_js()
    >>> web_view.page().runJavaScript(script)
"""


class JavaScriptInjector:
    """Provides JavaScript code for web player interaction and ad blocking.
    
    This class contains static methods that generate JavaScript snippets for
    controlling the embedded web player and blocking advertisements. Each method
    returns a complete, self-contained script that can be injected into a
    QWebEngineView.
    
    The scripts are designed to:
        - Work with YouTube and YouTube Music's current DOM structure
        - Gracefully degrade if expected elements aren't found
        - Have minimal performance impact
        - Log useful debugging information to console
    
    All methods are static as they don't require instance state and act as
    factories for JavaScript strings.
    
    Script Categories:
        - Ad blocking: CSS injection and DOM manipulation
        - Playback control: Button finding and keyboard events
        - Monitoring: MutationObserver for dynamic content
    
    Note:
        These scripts may need updates if YouTube significantly changes their
        HTML structure or CSS classes. The scripts include multiple fallback
        selectors to improve resilience.
    
    Examples:
        >>> injector = JavaScriptInjector()
        >>> play_pause_script = injector.get_play_pause_js()
        >>> web_view.page().runJavaScript(play_pause_script)
    """
    
    @staticmethod
    def get_ad_blocker_css():
        """Get early CSS injection for basic ad blocking.
        
        Returns CSS that hides common YouTube ad containers. This script
        should be injected at DocumentCreation stage (before page loads)
        for immediate ad hiding without flicker.
        
        Returns:
            str: JavaScript code that injects ad-blocking CSS into the page.
        
        Side Effects:
            - Adds a <style> element to the page head/documentElement
            - Applies display:none to ad container elements
        
        Examples:
            >>> script = JavaScriptInjector.get_ad_blocker_css()
            >>> page.runJavaScript(script, QWebEngineScript.DocumentCreation)
        """
        return """
            (function() {
                var css = '.video-ads, .ytp-ad-module, ytd-display-ad-renderer, ytd-ad-slot-renderer { display: none !important; }';
                var style = document.createElement('style');
                style.innerHTML = css;
                (document.head || document.documentElement).appendChild(style);
            })();
        """
    
    @staticmethod
    def get_ad_blocker_js():
        """Get comprehensive ad blocker with dynamic monitoring.
        
        Returns JavaScript that performs deep ad removal and sets up a
        MutationObserver to catch dynamically loaded ads. This should run
        after page load is complete (DocumentReady or Deferred).
        
        The script:
            - Injects comprehensive CSS rules hiding ad elements
            - Removes ad DOM elements from the page
            - Sets up MutationObserver to remove ads loaded later
            - Skips ads that appear in video players
        
        Returns:
            str: JavaScript code for comprehensive ad blocking.
        
        Side Effects:
            - Adds CSS style element to page
            - Removes ad elements from DOM
            - Installs MutationObserver that runs continuously
            - Logs actions to browser console
        
        Note:
            Targets YouTube and YouTube Music specific ad classes. May need
            updates if ad selectors change.
        
        Examples:
            >>> script = JavaScriptInjector.get_ad_blocker_js()
            >>> page.runJavaScript(script, QWebEngineScript.Deferred)
        """
        return """
            (function() {
                console.log('[Ad Blocker] Initializing');
                
                var css = document.createElement('style');
                css.innerHTML = `
                    ytd-display-ad-renderer, ytd-promoted-sparkles-web-renderer,
                    ytd-ad-slot-renderer, ytd-in-feed-ad-layout-renderer,
                    ytd-banner-promo-renderer, .video-ads, .ytp-ad-module,
                    ytd-popup-container, ytd-merch-shelf-renderer,
                    ytd-engagement-panel-section-list-renderer[target-id="engagement-panel-ads"],
                    #player-ads, .ytp-ad-overlay-container,
                    ytmusic-display-ad-renderer, ytmusic-companion-ad-renderer,
                    .ytp-ad-text, .ytp-ad-preview-container,
                    ytd-compact-promoted-item-renderer,
                    .ytd-promoted-video-renderer,
                    #masthead-ad, .ytd-action-companion-ad-renderer,
                    ytd-banner-promo-renderer-background,
                    ytd-statement-banner-renderer,
                    ytd-player-legacy-desktop-watch-ads-renderer
                    { display: none !important; visibility: hidden !important; }
                `;
                (document.head || document.documentElement).appendChild(css);
                
                function removeAds() {
                    var selectors = [
                        'ytd-display-ad-renderer', 'ytd-ad-slot-renderer', 
                        '.video-ads', 'ytmusic-display-ad-renderer',
                        '.ytp-ad-module', '#player-ads',
                        'ytd-banner-promo-renderer',
                        'ytd-compact-promoted-item-renderer',
                        '.ytd-promoted-video-renderer'
                    ];
                    selectors.forEach(function(sel) {
                        document.querySelectorAll(sel).forEach(function(el) {
                            el.remove();
                        });
                    });
                    
                    var video = document.querySelector('video');
                    if (video && video.duration > 0 && video.duration < 60) {
                        var adContainer = video.closest('.video-ads, .ytp-ad-module');
                        if (adContainer) {
                            video.currentTime = video.duration;
                        }
                    }
                }
                
                removeAds();
                setInterval(removeAds, 500);
                
                var observer = new MutationObserver(function() {
                    removeAds();
                });
                observer.observe(document.body, {
                    childList: true,
                    subtree: true
                });
                
                console.log('[Ad Blocker] Active');
            })();
        """
    
    @staticmethod
    def get_play_pause_js():
        """Get JavaScript for play/pause control."""
        return """
            (function() {
                var btn = document.querySelector('button[aria-label*="Play"]') ||
                          document.querySelector('button[aria-label*="Pause"]') ||
                          document.querySelector('.play-pause-button') ||
                          document.querySelector('#play-pause-button');
                if (btn) { btn.click(); return; }
                var evt = new KeyboardEvent('keydown', {
                    key: 'k', code: 'KeyK', keyCode: 75, which: 75, bubbles: true, cancelable: true
                });
                document.body.dispatchEvent(evt);
            })();
        """
    
    @staticmethod
    def get_next_track_js():
        """Get JavaScript for next track control."""
        return """
            (function() {
                var btn = document.querySelector('.next-button') ||
                          document.querySelector('button[aria-label*="Next"]') ||
                          document.querySelector('[aria-label*="Next track"]');
                if (btn) { btn.click(); return; }
                var evt = new KeyboardEvent('keydown', {
                    key: 'n', code: 'KeyN', keyCode: 78, which: 78,
                    shiftKey: true, bubbles: true, cancelable: true
                });
                document.body.dispatchEvent(evt);
            })();
        """
    
    @staticmethod
    def get_previous_track_js():
        """Get JavaScript for previous track control."""
        return """
            (function() {
                var btn = document.querySelector('.previous-button') ||
                          document.querySelector('button[aria-label*="Previous"]') ||
                          document.querySelector('[aria-label*="Previous track"]');
                if (btn) { btn.click(); return; }
                var evt = new KeyboardEvent('keydown', {
                    key: 'p', code: 'KeyP', keyCode: 80, which: 80,
                    shiftKey: true, bubbles: true, cancelable: true
                });
                document.body.dispatchEvent(evt);
            })();
        """
