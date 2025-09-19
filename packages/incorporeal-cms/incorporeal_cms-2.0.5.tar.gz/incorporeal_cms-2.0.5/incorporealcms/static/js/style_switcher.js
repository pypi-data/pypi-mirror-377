/**
 * Allow the user to change their desired styles dynamically despite the site being static.
 *
 * Loathe as I am to use JavaScript, this style selection is one of my favorite parts
 * of my CMS, so I want to keep it around even in the static site.
 *
 * SPDX-FileCopyrightText: © 2025 Brian S. Stephan <bss@incorporeal.org>
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

/**
 * Disable all stylesheets except the one to apply, the user style.
 */
function applyStyle(styleName) {
	var i, link_tag;
	for (i = 0, link_tag = document.getElementsByTagName("link"); i < link_tag.length; i++ ) {
		// find the stylesheets with titles, meaning they can be disabled/enabled
		if ((link_tag[i].rel.indexOf("stylesheet") != -1) && link_tag[i].title) {
			link_tag[i].disabled = true;
			if (link_tag[i].title == styleName) {
				link_tag[i].disabled = false ;
			}
		}
	}
}

/**
 * Set a cookie indicating the selected user style, and then switch to it.
 */
function setStyle(styleName) {
	document.cookie = "user-style=" + encodeURIComponent(styleName) +
		"; max-age=31536000;domain=" + window.location.hostname + ";path=/";
	applyStyle(styleName);
}

/**
 * Read the user's cookie, if they have one, and try to set the style to the one specified.
 */
function applyStyleFromCookie() {
	// get the user style cookie and set that specified style as the active one
	var styleName = getCookie("user-style");
	if (styleName) {
		applyStyle(styleName);
	}
}

/**
 * Get the user style cookie.
 */
function getCookie(cookieName) {
	// find the desired cookie from the document's cookie(s) string
	let matches = document.cookie.match(new RegExp(
		"(?:^|; )" + cookieName.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
	));
	return matches ? decodeURIComponent(matches[1]) : undefined;
}

// auto apply the style on load
applyStyleFromCookie();
