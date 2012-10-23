/*jslint plusplus: true */
/*global $, alert, document, portal_url, setTimeout */
(function () {
    "use strict";

    var SLIDEUP_MS,   // slideUp effect duration for hiding table rows on @@cart
        STATUS,       // response status codes
        isCartView,   // set to true when on @@cart view
        nItems,       // the number of items currently in cart
        $cartLink;    // jQuery reference to cart link in the personaltools menu

    SLIDEUP_MS = 1000;

    STATUS = {
        OK: 0,
        ERROR: 1
    };

    function updateCartLabel() {
        var lastPart,   // last chunk of the text
            parts;      // parts of the split text

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

    // retrieve the number of items in cart from the server and update the
    // cart label in personaltools menu along the way
    function updateItemCount() {
        var onSuccess,
            url;

        url = portal_url + "/cart/item_count";
        onSuccess = function (data) {
            nItems = (data.status === STATUS.OK) ?
                      parseInt(data.body, 10) : "error";
            updateCartLabel();
        };

        $.getJSON(url, onSuccess);
    }


    function removeItem($link) {

        var $nextRows,
            $row;

        if (nItems <= 0) {
            // some kind of an UI error, trying to remove items when the cart is empty
            // TODO: log to console?
            alert("An attempt to remove an item while the cart is empty");
            return;
        }

        // a helper function for flipping the table row parity classes
        function flipParityClasses($rowList) {
            $rowList.each(function () {
                $row = $(this);
                if ($row.hasClass("odd")) {
                    $row.addClass("even");
                    $row.removeClass("odd");
                } else {  // even row
                    $row.addClass("odd");
                    $row.removeClass("even");
                }
            });
        }

        $.getJSON($link.attr("href"), function (data) {
            if (data.status !== STATUS.OK) {
                //TODO: log to console?
                alert("server error deleting item");
                return;
            }

            nItems--;
            updateCartLabel();

            if (isCartView) {
                $row = $($link.parents("tr")[0]);  // must wrap into jQuery object
                $nextRows = $row.nextAll();

                //TODO: for some reason the animation is not working in FF 16.0.1
                $row.slideUp(SLIDEUP_MS, "linear", function () {
                    $(this).remove();
                });

                //flip parity classes of all the rows below (odd to even, even to odd)
                setTimeout(function () {
                    flipParityClasses($nextRows);
                }, SLIDEUP_MS);   // should be the same delay as for the slideUp effect

            } else {
                //TODO: transform $link from "remove from cart" to "add to cart"
                // (this is only for views other than @@cart
                alert("not implemented yet");
            }
        });  //end getJSON
    }

    // initialize click handlers for the links for adding/removing
    // things from the cart
    function initLinks() {

        // links from removing things from the cart
        $("a.remove-from-cart").each(function () {
            $(this).click(function (event) {
                event.preventDefault();
                removeItem($(this));
            });
        });

        // TODO: the same for links for adding stuff to cart and for clearing the cart
    }

    $("document").ready(function () {
        // right trim - trim all whitespace at the end of the string
        String.prototype.rtrim = function () {
            return this.replace(/\s+$/, "");
        };

        $cartLink = $("#personaltools-cart > a");
        isCartView = $("body.template-cart").length > 0;

        initLinks();

        updateItemCount();
    });

}());
