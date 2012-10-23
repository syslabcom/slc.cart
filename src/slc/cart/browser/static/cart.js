/*global $, document, portal_url*/
(function () {
    "use strict";

    var nItems,      //the number of items currently in cart
        $cartLink;   //jQuery reference to cart link in the personaltools menu

    function updateCartLabel() {
        var lastPart,   //last chunk of the text
            parts;      //parts of the split text

        if ($cartLink.length < 1) {
            return;  // element not present in DOM, do nothing
        }

        // An example of of the cart link text:
        //
        // Cart Name in Whatever Language (42)
        //
        parts = $cartLink.text().split(" ");

        lastPart = ["(", nItems, ")"].join("");
        parts[parts.length - 1] = lastPart;

        $cartLink.text(parts.join(" ").rtrim());
    }

    function updateItemCount(pollServer) {
        var onSuccess,
            url;

        if (pollServer === undefined) {
            pollServer = false;
        }

        if (!pollServer) {
            updateCartLabel();
            return;
        }

        url = portal_url + "/cart/item_count";
        onSuccess = function (data) {
            nItems = parseInt(data, 10);
            updateCartLabel();
        };

        $.get(url, onSuccess);
    }

    $("document").ready(function () {
        // right trim - trim all whitespace at the end of the string
        String.prototype.rtrim = function () {
            return this.replace(/\s+$/, "");
        };

        $cartLink = $("#personaltools-cart > a");

        updateItemCount(true);
    });

}());
