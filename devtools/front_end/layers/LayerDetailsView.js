/*
 * Copyright (C) 2013 Google Inc. All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met:
 *
 *     * Redistributions of source code must retain the above copyright
 * notice, this list of conditions and the following disclaimer.
 *     * Redistributions in binary form must reproduce the above
 * copyright notice, this list of conditions and the following disclaimer
 * in the documentation and/or other materials provided with the
 * distribution.
 *     * Neither the name of Google Inc. nor the names of its
 * contributors may be used to endorse or promote products derived from
 * this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 * A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 * OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

/**
 * @constructor
 * @extends {WebInspector.VBox}
 */
WebInspector.LayerDetailsView = function()
{
    WebInspector.VBox.call(this);
    this.element.classList.add("layer-details-view");
    this._emptyView = new WebInspector.EmptyView(WebInspector.UIString("Select a layer or tile to see its details"));
    this._createTable();
}

/**
 * @enum {string}
 */
WebInspector.LayerDetailsView.Events = {
    ObjectSelected: "ObjectSelected"
}

/**
 * @enum {string}
 */
WebInspector.LayerDetailsView.Type = {
    Layer: "Layer",
    Tile: "Tile",
    All: "All"
}

/**
 * @type {!Object.<string, string>}
 */
WebInspector.LayerDetailsView.CompositingReasonDetail = {
    "transform3D": WebInspector.UIString("Composition due to association with an element with a CSS 3D transform."),
    "video": WebInspector.UIString("Composition due to association with a <video> element."),
    "canvas": WebInspector.UIString("Composition due to the element being a <canvas> element."),
    "plugin": WebInspector.UIString("Composition due to association with a plugin."),
    "iFrame": WebInspector.UIString("Composition due to association with an <iframe> element."),
    "backfaceVisibilityHidden": WebInspector.UIString("Composition due to association with an element with a \"backface-visibility: hidden\" style."),
    "animation": WebInspector.UIString("Composition due to association with an animated element."),
    "filters": WebInspector.UIString("Composition due to association with an element with CSS filters applied."),
    "positionFixed": WebInspector.UIString("Composition due to association with an element with a \"position: fixed\" style."),
    // FIXME: Can we remove this entry now that position: sticky has been removed?
    "positionSticky": WebInspector.UIString("Composition due to association with an element with a \"position: sticky\" style."),
    "overflowScrollingTouch": WebInspector.UIString("Composition due to association with an element with a \"overflow-scrolling: touch\" style."),
    "blending": WebInspector.UIString("Composition due to association with an element that has blend mode other than \"normal\"."),
    "assumedOverlap": WebInspector.UIString("Composition due to association with an element that may overlap other composited elements."),
    "overlap": WebInspector.UIString("Composition due to association with an element overlapping other composited elements."),
    "negativeZIndexChildren": WebInspector.UIString("Composition due to association with an element with descendants that have a negative z-index."),
    "transformWithCompositedDescendants": WebInspector.UIString("Composition due to association with an element with composited descendants."),
    "opacityWithCompositedDescendants": WebInspector.UIString("Composition due to association with an element with opacity applied and composited descendants."),
    "maskWithCompositedDescendants": WebInspector.UIString("Composition due to association with a masked element and composited descendants."),
    "reflectionWithCompositedDescendants": WebInspector.UIString("Composition due to association with an element with a reflection and composited descendants."),
    "filterWithCompositedDescendants": WebInspector.UIString("Composition due to association with an element with CSS filters applied and composited descendants."),
    "blendingWithCompositedDescendants": WebInspector.UIString("Composition due to association with an element with CSS blending applied and composited descendants."),
    "clipsCompositingDescendants": WebInspector.UIString("Composition due to association with an element clipping compositing descendants."),
    "perspective": WebInspector.UIString("Composition due to association with an element with perspective applied."),
    "preserve3D": WebInspector.UIString("Composition due to association with an element with a \"transform-style: preserve-3d\" style."),
    "root": WebInspector.UIString("Root layer."),
    "layerForClip": WebInspector.UIString("Layer for clip."),
    "layerForScrollbar": WebInspector.UIString("Layer for scrollbar."),
    "layerForScrollingContainer": WebInspector.UIString("Layer for scrolling container."),
    "layerForForeground": WebInspector.UIString("Layer for foreground."),
    "layerForBackground": WebInspector.UIString("Layer for background."),
    "layerForMask": WebInspector.UIString("Layer for mask."),
    "layerForVideoOverlay": WebInspector.UIString("Layer for video overlay.")
};

WebInspector.LayerDetailsView.prototype = {
    /**
     * @param {!WebInspector.Layers3DView.ActiveObject} activeObject
     */
    setObject: function(activeObject)
    {
        if (!activeObject) {
            this._layer = null;
            this._tile = null;
            if (this.isShowing())
                this.update(WebInspector.LayerDetailsView.Type.Layer);
            return;
        }

        if (activeObject.type() == WebInspector.Layers3DView.ActiveObject.Type.Layer) {
            this._layer = activeObject.layer;
            this._scrollRectIndex = activeObject ? activeObject.scrollRectIndex : null;
            if (this.isShowing())
                this.update(WebInspector.LayerDetailsView.Type.Layer);
        } else if (activeObject.type() == WebInspector.Layers3DView.ActiveObject.Type.Tile) {
            this._tile = activeObject.tile;
            if (this.isShowing())
                this.update(WebInspector.LayerDetailsView.Type.Tile);
        }
    },

    wasShown: function()
    {
        WebInspector.View.prototype.wasShown.call(this);
        this.update(WebInspector.LayerDetailsView.Type.Layer);
    },

    /**
     * @param {number} index
     * @param {!Event} event
     */
    _onScrollRectClicked: function(index, event)
    {
        if (event.which !== 1)
            return;
        this.dispatchEventToListeners(WebInspector.LayerDetailsView.Events.ObjectSelected, {layer: this._layer, scrollRectIndex: index});
    },

    /**
     * @param {!LayerTreeAgent.ScrollRect} scrollRect
     * @param {number} index
     */
    _createScrollRectElement: function(scrollRect, index)
    {
        if (index)
            this._scrollRectsCell.createTextChild(", ");
        var element = this._scrollRectsCell.createChild("span");
        element.className = index === this._scrollRectIndex ? "scroll-rect active" : "scroll-rect";
        element.textContent = WebInspector.LayerTreeModel.ScrollRectType[scrollRect.type].description + " (" + scrollRect.rect.x + ", " + scrollRect.rect.y +
            ", " + scrollRect.rect.width + ", " + scrollRect.rect.height + ")";
        element.addEventListener("click", this._onScrollRectClicked.bind(this, index), false);
    },

    update: function(type)
    {
        if (type === WebInspector.LayerDetailsView.Type.All || type === WebInspector.LayerDetailsView.Type.Layer) {
            if (!this._layer) {
                this._layerTableElement.remove();
                this._emptyView.show(this.element);
            }
            if (this._layer) {
                this._tileTableElement.remove();
                this._emptyView.detach();
                this.element.appendChild(this._layerTableElement);
                this._layerPositionCell.textContent = WebInspector.UIString("%d,%d", this._layer.offsetX(), this._layer.offsetY());
                this._layerSizeCell.textContent = WebInspector.UIString("%d × %d", this._layer.width(), this._layer.height());
                this._paintCountCell.textContent = this._layer.paintCount();
                const bytesPerPixel = 4;
                this._memoryEstimateCell.textContent = Number.bytesToString(this._layer.invisible() ? 0 : this._layer.width() * this._layer.height() * bytesPerPixel);
                this._layer.requestCompositingReasons(this._updateCompositingReasons.bind(this));
                this._scrollRectsCell.removeChildren();
                this._layer.scrollRects().forEach(this._createScrollRectElement.bind(this));
            }
        }

        if (type === WebInspector.LayerDetailsView.Type.All || type === WebInspector.LayerDetailsView.Type.Tile) {
            if (!this._tile) {
                this._tileTableElement.remove();
                this._emptyView.show(this.element);
            }
            if (this._tile) {
                this._layerTableElement.remove();
                this._emptyView.detach();
                this.element.appendChild(this._tileTableElement);
                this._idCell.textContent = WebInspector.UIString("%s", this._tile.id);
                this._tilePositionCell.textContent = WebInspector.UIString("%d,%d", this._tile.rect.x, this._tile.rect.y);
                this._tileSizeCell.textContent = WebInspector.UIString("%d × %d", this._tile.rect.width, this._tile.rect.height);
                this._rasterModeCell.textContent = WebInspector.UIString("%s", this._tile.rasterMode);
                this._scaleCell.textContent = WebInspector.UIString("%d", this._tile.scale);
            }
        }
    },

    _createTable: function()
    {
        this._layerTableElement = this.element.createChild("table");
        this._tlayerbodyElement = this._layerTableElement.createChild("tbody");
        this._layerPositionCell = this._createRow(WebInspector.UIString("Position in parent:"), this._tlayerbodyElement);
        this._layerSizeCell = this._createRow(WebInspector.UIString("Size:"), this._tlayerbodyElement);
        this._compositingReasonsCell = this._createRow(WebInspector.UIString("Compositing Reasons:"), this._tlayerbodyElement);
        this._memoryEstimateCell = this._createRow(WebInspector.UIString("Memory estimate:"), this._tlayerbodyElement);
        this._paintCountCell = this._createRow(WebInspector.UIString("Paint count:"), this._tlayerbodyElement);
        this._scrollRectsCell = this._createRow(WebInspector.UIString("Slow scroll regions:"), this._tlayerbodyElement);

        // For Tile
        this._tileTableElement = this.element.createChild("table");
        this._ttilebodyElement = this._tileTableElement.createChild("tbody");
        this._idCell = this._createRow(WebInspector.UIString("ID:"), this._ttilebodyElement);
        this._tilePositionCell = this._createRow(WebInspector.UIString("Position:"), this._ttilebodyElement);
        this._tileSizeCell = this._createRow(WebInspector.UIString("Size:"), this._ttilebodyElement);
        this._rasterModeCell = this._createRow(WebInspector.UIString("Raster mode:"), this._ttilebodyElement);
        this._scaleCell = this._createRow(WebInspector.UIString("Scale:"), this._ttilebodyElement);
    },

    /**
     * @param {string} title
     */
    _createRow: function(title, bodyElement)
    {
        var tr = bodyElement.createChild("tr");
        var titleCell = tr.createChild("td");
        titleCell.textContent = title;
        return tr.createChild("td");
    },

    /**
     * @param {!Array.<string>} compositingReasons
     */
    _updateCompositingReasons: function(compositingReasons)
    {
        if (!compositingReasons || !compositingReasons.length) {
            this._compositingReasonsCell.textContent = "n/a";
            return;
        }
        var fragment = document.createDocumentFragment();
        for (var i = 0; i < compositingReasons.length; ++i) {
            if (i)
                fragment.appendChild(document.createTextNode(","));
            var span = document.createElement("span");
            span.title = WebInspector.LayerDetailsView.CompositingReasonDetail[compositingReasons[i]] || "";
            span.textContent = compositingReasons[i];
            fragment.appendChild(span);
        }
        this._compositingReasonsCell.removeChildren();
        this._compositingReasonsCell.appendChild(fragment);
    },

    __proto__: WebInspector.VBox.prototype
}
