/*!
 * jQuery UI 1.8.12
 *
 * Copyright 2011, AUTHORS.txt (http://jqueryui.com/about)
 * Dual licensed under the MIT or GPL Version 2 licenses.
 * http://jquery.org/license
 *
 * http://docs.jquery.com/UI
 */
(function( $, undefined ) {

// prevent duplicate loading
// this is only a problem because we proxy existing functions
// and we don't want to double proxy them
$.ui = $.ui || {};
if ( $.ui.version ) {
	return;
}

$.extend( $.ui, {
	version: "1.8.12",

	keyCode: {
		ALT: 18,
		BACKSPACE: 8,
		CAPS_LOCK: 20,
		COMMA: 188,
		COMMAND: 91,
		COMMAND_LEFT: 91, // COMMAND
		COMMAND_RIGHT: 93,
		CONTROL: 17,
		DELETE: 46,
		DOWN: 40,
		END: 35,
		ENTER: 13,
		ESCAPE: 27,
		HOME: 36,
		INSERT: 45,
		LEFT: 37,
		MENU: 93, // COMMAND_RIGHT
		NUMPAD_ADD: 107,
		NUMPAD_DECIMAL: 110,
		NUMPAD_DIVIDE: 111,
		NUMPAD_ENTER: 108,
		NUMPAD_MULTIPLY: 106,
		NUMPAD_SUBTRACT: 109,
		PAGE_DOWN: 34,
		PAGE_UP: 33,
		PERIOD: 190,
		RIGHT: 39,
		SHIFT: 16,
		SPACE: 32,
		TAB: 9,
		UP: 38,
		WINDOWS: 91 // COMMAND
	}
});

// plugins
$.fn.extend({
	_focus: $.fn.focus,
	focus: function( delay, fn ) {
		return typeof delay === "number" ?
			this.each(function() {
				var elem = this;
				setTimeout(function() {
					$( elem ).focus();
					if ( fn ) {
						fn.call( elem );
					}
				}, delay );
			}) :
			this._focus.apply( this, arguments );
	},

	scrollParent: function() {
		var scrollParent;
		if (($.browser.msie && (/(static|relative)/).test(this.css('position'))) || (/absolute/).test(this.css('position'))) {
			scrollParent = this.parents().filter(function() {
				return (/(relative|absolute|fixed)/).test($.curCSS(this,'position',1)) && (/(auto|scroll)/).test($.curCSS(this,'overflow',1)+$.curCSS(this,'overflow-y',1)+$.curCSS(this,'overflow-x',1));
			}).eq(0);
		} else {
			scrollParent = this.parents().filter(function() {
				return (/(auto|scroll)/).test($.curCSS(this,'overflow',1)+$.curCSS(this,'overflow-y',1)+$.curCSS(this,'overflow-x',1));
			}).eq(0);
		}

		return (/fixed/).test(this.css('position')) || !scrollParent.length ? $(document) : scrollParent;
	},

	zIndex: function( zIndex ) {
		if ( zIndex !== undefined ) {
			return this.css( "zIndex", zIndex );
		}

		if ( this.length ) {
			var elem = $( this[ 0 ] ), position, value;
			while ( elem.length && elem[ 0 ] !== document ) {
				// Ignore z-index if position is set to a value where z-index is ignored by the browser
				// This makes behavior of this function consistent across browsers
				// WebKit always returns auto if the element is positioned
				position = elem.css( "position" );
				if ( position === "absolute" || position === "relative" || position === "fixed" ) {
					// IE returns 0 when zIndex is not specified
					// other browsers return a string
					// we ignore the case of nested elements with an explicit value of 0
					// <div style="z-index: -10;"><div style="z-index: 0;"></div></div>
					value = parseInt( elem.css( "zIndex" ), 10 );
					if ( !isNaN( value ) && value !== 0 ) {
						return value;
					}
				}
				elem = elem.parent();
			}
		}

		return 0;
	},

	disableSelection: function() {
		return this.bind( ( $.support.selectstart ? "selectstart" : "mousedown" ) +
			".ui-disableSelection", function( event ) {
				event.preventDefault();
			});
	},

	enableSelection: function() {
		return this.unbind( ".ui-disableSelection" );
	}
});

$.each( [ "Width", "Height" ], function( i, name ) {
	var side = name === "Width" ? [ "Left", "Right" ] : [ "Top", "Bottom" ],
		type = name.toLowerCase(),
		orig = {
			innerWidth: $.fn.innerWidth,
			innerHeight: $.fn.innerHeight,
			outerWidth: $.fn.outerWidth,
			outerHeight: $.fn.outerHeight
		};

	function reduce( elem, size, border, margin ) {
		$.each( side, function() {
			size -= parseFloat( $.curCSS( elem, "padding" + this, true) ) || 0;
			if ( border ) {
				size -= parseFloat( $.curCSS( elem, "border" + this + "Width", true) ) || 0;
			}
			if ( margin ) {
				size -= parseFloat( $.curCSS( elem, "margin" + this, true) ) || 0;
			}
		});
		return size;
	}

	$.fn[ "inner" + name ] = function( size ) {
		if ( size === undefined ) {
			return orig[ "inner" + name ].call( this );
		}

		return this.each(function() {
			$( this ).css( type, reduce( this, size ) + "px" );
		});
	};

	$.fn[ "outer" + name] = function( size, margin ) {
		if ( typeof size !== "number" ) {
			return orig[ "outer" + name ].call( this, size );
		}

		return this.each(function() {
			$( this).css( type, reduce( this, size, true, margin ) + "px" );
		});
	};
});

// selectors
function visible( element ) {
	return !$( element ).parents().andSelf().filter(function() {
		return $.curCSS( this, "visibility" ) === "hidden" ||
			$.expr.filters.hidden( this );
	}).length;
}

$.extend( $.expr[ ":" ], {
	data: function( elem, i, match ) {
		return !!$.data( elem, match[ 3 ] );
	},

	focusable: function( element ) {
		var nodeName = element.nodeName.toLowerCase(),
			tabIndex = $.attr( element, "tabindex" );
		if ( "area" === nodeName ) {
			var map = element.parentNode,
				mapName = map.name,
				img;
			if ( !element.href || !mapName || map.nodeName.toLowerCase() !== "map" ) {
				return false;
			}
			img = $( "img[usemap=#" + mapName + "]" )[0];
			return !!img && visible( img );
		}
		return ( /input|select|textarea|button|object/.test( nodeName )
			? !element.disabled
			: "a" == nodeName
				? element.href || !isNaN( tabIndex )
				: !isNaN( tabIndex ))
			// the element and all of its ancestors must be visible
			&& visible( element );
	},

	tabbable: function( element ) {
		var tabIndex = $.attr( element, "tabindex" );
		return ( isNaN( tabIndex ) || tabIndex >= 0 ) && $( element ).is( ":focusable" );
	}
});

// support
$(function() {
	var body = document.body,
		div = body.appendChild( div = document.createElement( "div" ) );

	$.extend( div.style, {
		minHeight: "100px",
		height: "auto",
		padding: 0,
		borderWidth: 0
	});

	$.support.minHeight = div.offsetHeight === 100;
	$.support.selectstart = "onselectstart" in div;

	// set display to none to avoid a layout bug in IE
	// http://dev.jquery.com/ticket/4014
	body.removeChild( div ).style.display = "none";
});





// deprecated
$.extend( $.ui, {
	// $.ui.plugin is deprecated.  Use the proxy pattern instead.
	plugin: {
		add: function( module, option, set ) {
			var proto = $.ui[ module ].prototype;
			for ( var i in set ) {
				proto.plugins[ i ] = proto.plugins[ i ] || [];
				proto.plugins[ i ].push( [ option, set[ i ] ] );
			}
		},
		call: function( instance, name, args ) {
			var set = instance.plugins[ name ];
			if ( !set || !instance.element[ 0 ].parentNode ) {
				return;
			}
	
			for ( var i = 0; i < set.length; i++ ) {
				if ( instance.options[ set[ i ][ 0 ] ] ) {
					set[ i ][ 1 ].apply( instance.element, args );
				}
			}
		}
	},
	
	// will be deprecated when we switch to jQuery 1.4 - use jQuery.contains()
	contains: function( a, b ) {
		return document.compareDocumentPosition ?
			a.compareDocumentPosition( b ) & 16 :
			a !== b && a.contains( b );
	},
	
	// only used by resizable
	hasScroll: function( el, a ) {
	
		//If overflow is hidden, the element might have extra content, but the user wants to hide it
		if ( $( el ).css( "overflow" ) === "hidden") {
			return false;
		}
	
		var scroll = ( a && a === "left" ) ? "scrollLeft" : "scrollTop",
			has = false;
	
		if ( el[ scroll ] > 0 ) {
			return true;
		}
	
		// TODO: determine which cases actually cause this to happen
		// if the element doesn't have the scroll set, see if it's possible to
		// set the scroll
		el[ scroll ] = 1;
		has = ( el[ scroll ] > 0 );
		el[ scroll ] = 0;
		return has;
	},
	
	// these are odd functions, fix the API or move into individual plugins
	isOverAxis: function( x, reference, size ) {
		//Determines when x coordinate is over "b" element axis
		return ( x > reference ) && ( x < ( reference + size ) );
	},
	isOver: function( y, x, top, left, height, width ) {
		//Determines when x, y coordinates is over "b" element
		return $.ui.isOverAxis( y, top, height ) && $.ui.isOverAxis( x, left, width );
	}
});

})( jQuery );
/*!
 * jQuery UI Widget 1.8.12
 *
 * Copyright 2011, AUTHORS.txt (http://jqueryui.com/about)
 * Dual licensed under the MIT or GPL Version 2 licenses.
 * http://jquery.org/license
 *
 * http://docs.jquery.com/UI/Widget
 */
(function( $, undefined ) {

// jQuery 1.4+
if ( $.cleanData ) {
	var _cleanData = $.cleanData;
	$.cleanData = function( elems ) {
		for ( var i = 0, elem; (elem = elems[i]) != null; i++ ) {
			$( elem ).triggerHandler( "remove" );
		}
		_cleanData( elems );
	};
} else {
	var _remove = $.fn.remove;
	$.fn.remove = function( selector, keepData ) {
		return this.each(function() {
			if ( !keepData ) {
				if ( !selector || $.filter( selector, [ this ] ).length ) {
					$( "*", this ).add( [ this ] ).each(function() {
						$( this ).triggerHandler( "remove" );
					});
				}
			}
			return _remove.call( $(this), selector, keepData );
		});
	};
}

$.widget = function( name, base, prototype ) {
	var namespace = name.split( "." )[ 0 ],
		fullName;
	name = name.split( "." )[ 1 ];
	fullName = namespace + "-" + name;

	if ( !prototype ) {
		prototype = base;
		base = $.Widget;
	}

	// create selector for plugin
	$.expr[ ":" ][ fullName ] = function( elem ) {
		return !!$.data( elem, name );
	};

	$[ namespace ] = $[ namespace ] || {};
	$[ namespace ][ name ] = function( options, element ) {
		// allow instantiation without initializing for simple inheritance
		if ( arguments.length ) {
			this._createWidget( options, element );
		}
	};

	var basePrototype = new base();
	// we need to make the options hash a property directly on the new instance
	// otherwise we'll modify the options hash on the prototype that we're
	// inheriting from
//	$.each( basePrototype, function( key, val ) {
//		if ( $.isPlainObject(val) ) {
//			basePrototype[ key ] = $.extend( {}, val );
//		}
//	});
	basePrototype.options = $.extend( true, {}, basePrototype.options );
	$[ namespace ][ name ].prototype = $.extend( true, basePrototype, {
		namespace: namespace,
		widgetName: name,
		widgetEventPrefix: $[ namespace ][ name ].prototype.widgetEventPrefix || name,
		widgetBaseClass: fullName
	}, prototype );

	$.widget.bridge( name, $[ namespace ][ name ] );
};

$.widget.bridge = function( name, object ) {
	$.fn[ name ] = function( options ) {
		var isMethodCall = typeof options === "string",
			args = Array.prototype.slice.call( arguments, 1 ),
			returnValue = this;

		// allow multiple hashes to be passed on init
		options = !isMethodCall && args.length ?
			$.extend.apply( null, [ true, options ].concat(args) ) :
			options;

		// prevent calls to internal methods
		if ( isMethodCall && options.charAt( 0 ) === "_" ) {
			return returnValue;
		}

		if ( isMethodCall ) {
			this.each(function() {
				var instance = $.data( this, name ),
					methodValue = instance && $.isFunction( instance[options] ) ?
						instance[ options ].apply( instance, args ) :
						instance;
				// TODO: add this back in 1.9 and use $.error() (see #5972)
//				if ( !instance ) {
//					throw "cannot call methods on " + name + " prior to initialization; " +
//						"attempted to call method '" + options + "'";
//				}
//				if ( !$.isFunction( instance[options] ) ) {
//					throw "no such method '" + options + "' for " + name + " widget instance";
//				}
//				var methodValue = instance[ options ].apply( instance, args );
				if ( methodValue !== instance && methodValue !== undefined ) {
					returnValue = methodValue;
					return false;
				}
			});
		} else {
			this.each(function() {
				var instance = $.data( this, name );
				if ( instance ) {
					instance.option( options || {} )._init();
				} else {
					$.data( this, name, new object( options, this ) );
				}
			});
		}

		return returnValue;
	};
};

$.Widget = function( options, element ) {
	// allow instantiation without initializing for simple inheritance
	if ( arguments.length ) {
		this._createWidget( options, element );
	}
};

$.Widget.prototype = {
	widgetName: "widget",
	widgetEventPrefix: "",
	options: {
		disabled: false
	},
	_createWidget: function( options, element ) {
		// $.widget.bridge stores the plugin instance, but we do it anyway
		// so that it's stored even before the _create function runs
		$.data( element, this.widgetName, this );
		this.element = $( element );
		this.options = $.extend( true, {},
			this.options,
			this._getCreateOptions(),
			options );

		var self = this;
		this.element.bind( "remove." + this.widgetName, function() {
			self.destroy();
		});

		this._create();
		this._trigger( "create" );
		this._init();
	},
	_getCreateOptions: function() {
		return $.metadata && $.metadata.get( this.element[0] )[ this.widgetName ];
	},
	_create: function() {},
	_init: function() {},

	destroy: function() {
		this.element
			.unbind( "." + this.widgetName )
			.removeData( this.widgetName );
		this.widget()
			.unbind( "." + this.widgetName )
			.removeAttr( "aria-disabled" )
			.removeClass(
				this.widgetBaseClass + "-disabled " +
				"ui-state-disabled" );
	},

	widget: function() {
		return this.element;
	},

	option: function( key, value ) {
		var options = key;

		if ( arguments.length === 0 ) {
			// don't return a reference to the internal hash
			return $.extend( {}, this.options );
		}

		if  (typeof key === "string" ) {
			if ( value === undefined ) {
				return this.options[ key ];
			}
			options = {};
			options[ key ] = value;
		}

		this._setOptions( options );

		return this;
	},
	_setOptions: function( options ) {
		var self = this;
		$.each( options, function( key, value ) {
			self._setOption( key, value );
		});

		return this;
	},
	_setOption: function( key, value ) {
		this.options[ key ] = value;

		if ( key === "disabled" ) {
			this.widget()
				[ value ? "addClass" : "removeClass"](
					this.widgetBaseClass + "-disabled" + " " +
					"ui-state-disabled" )
				.attr( "aria-disabled", value );
		}

		return this;
	},

	enable: function() {
		return this._setOption( "disabled", false );
	},
	disable: function() {
		return this._setOption( "disabled", true );
	},

	_trigger: function( type, event, data ) {
		var callback = this.options[ type ];

		event = $.Event( event );
		event.type = ( type === this.widgetEventPrefix ?
			type :
			this.widgetEventPrefix + type ).toLowerCase();
		data = data || {};

		// copy original event properties over to the new event
		// this would happen if we could call $.event.fix instead of $.Event
		// but we don't have a way to force an event to be fixed multiple times
		if ( event.originalEvent ) {
			for ( var i = $.event.props.length, prop; i; ) {
				prop = $.event.props[ --i ];
				event[ prop ] = event.originalEvent[ prop ];
			}
		}

		this.element.trigger( event, data );

		return !( $.isFunction(callback) &&
			callback.call( this.element[0], event, data ) === false ||
			event.isDefaultPrevented() );
	}
};

})( jQuery );
/*!
 * jQuery UI Mouse 1.8.12
 *
 * Copyright 2011, AUTHORS.txt (http://jqueryui.com/about)
 * Dual licensed under the MIT or GPL Version 2 licenses.
 * http://jquery.org/license
 *
 * http://docs.jquery.com/UI/Mouse
 *
 * Depends:
 *	jquery.ui.widget.js
 */
(function( $, undefined ) {

$.widget("ui.mouse", {
	options: {
		cancel: ':input,option',
		distance: 1,
		delay: 0
	},
	_mouseInit: function() {
		var self = this;

		this.element
			.bind('mousedown.'+this.widgetName, function(event) {
				return self._mouseDown(event);
			})
			.bind('click.'+this.widgetName, function(event) {
				if (true === $.data(event.target, self.widgetName + '.preventClickEvent')) {
				    $.removeData(event.target, self.widgetName + '.preventClickEvent');
					event.stopImmediatePropagation();
					return false;
				}
			});

		this.started = false;
	},

	// TODO: make sure destroying one instance of mouse doesn't mess with
	// other instances of mouse
	_mouseDestroy: function() {
		this.element.unbind('.'+this.widgetName);
	},

	_mouseDown: function(event) {
		// don't let more than one widget handle mouseStart
		// TODO: figure out why we have to use originalEvent
		event.originalEvent = event.originalEvent || {};
		if (event.originalEvent.mouseHandled) { return; }

		// we may have missed mouseup (out of window)
		(this._mouseStarted && this._mouseUp(event));

		this._mouseDownEvent = event;

		var self = this,
			btnIsLeft = (event.which == 1),
			elIsCancel = (typeof this.options.cancel == "string" ? $(event.target).parents().add(event.target).filter(this.options.cancel).length : false);
		if (!btnIsLeft || elIsCancel || !this._mouseCapture(event)) {
			return true;
		}

		this.mouseDelayMet = !this.options.delay;
		if (!this.mouseDelayMet) {
			this._mouseDelayTimer = setTimeout(function() {
				self.mouseDelayMet = true;
			}, this.options.delay);
		}

		if (this._mouseDistanceMet(event) && this._mouseDelayMet(event)) {
			this._mouseStarted = (this._mouseStart(event) !== false);
			if (!this._mouseStarted) {
				event.preventDefault();
				return true;
			}
		}

		// Click event may never have fired (Gecko & Opera)
		if (true === $.data(event.target, this.widgetName + '.preventClickEvent')) {
			$.removeData(event.target, this.widgetName + '.preventClickEvent');
		}

		// these delegates are required to keep context
		this._mouseMoveDelegate = function(event) {
			return self._mouseMove(event);
		};
		this._mouseUpDelegate = function(event) {
			return self._mouseUp(event);
		};
		$(document)
			.bind('mousemove.'+this.widgetName, this._mouseMoveDelegate)
			.bind('mouseup.'+this.widgetName, this._mouseUpDelegate);

		event.preventDefault();
		event.originalEvent.mouseHandled = true;
		return true;
	},

	_mouseMove: function(event) {
		// IE mouseup check - mouseup happened when mouse was out of window
		if ($.browser.msie && !(document.documentMode >= 9) && !event.button) {
			return this._mouseUp(event);
		}

		if (this._mouseStarted) {
			this._mouseDrag(event);
			return event.preventDefault();
		}

		if (this._mouseDistanceMet(event) && this._mouseDelayMet(event)) {
			this._mouseStarted =
				(this._mouseStart(this._mouseDownEvent, event) !== false);
			(this._mouseStarted ? this._mouseDrag(event) : this._mouseUp(event));
		}

		return !this._mouseStarted;
	},

	_mouseUp: function(event) {
		$(document)
			.unbind('mousemove.'+this.widgetName, this._mouseMoveDelegate)
			.unbind('mouseup.'+this.widgetName, this._mouseUpDelegate);

		if (this._mouseStarted) {
			this._mouseStarted = false;

			if (event.target == this._mouseDownEvent.target) {
			    $.data(event.target, this.widgetName + '.preventClickEvent', true);
			}

			this._mouseStop(event);
		}

		return false;
	},

	_mouseDistanceMet: function(event) {
		return (Math.max(
				Math.abs(this._mouseDownEvent.pageX - event.pageX),
				Math.abs(this._mouseDownEvent.pageY - event.pageY)
			) >= this.options.distance
		);
	},

	_mouseDelayMet: function(event) {
		return this.mouseDelayMet;
	},

	// These are placeholder methods, to be overriden by extending plugin
	_mouseStart: function(event) {},
	_mouseDrag: function(event) {},
	_mouseStop: function(event) {},
	_mouseCapture: function(event) { return true; }
});

})(jQuery);
/*
 * jQuery UI Position 1.8.12
 *
 * Copyright 2011, AUTHORS.txt (http://jqueryui.com/about)
 * Dual licensed under the MIT or GPL Version 2 licenses.
 * http://jquery.org/license
 *
 * http://docs.jquery.com/UI/Position
 */
(function( $, undefined ) {

$.ui = $.ui || {};

var horizontalPositions = /left|center|right/,
	verticalPositions = /top|center|bottom/,
	center = "center",
	_position = $.fn.position,
	_offset = $.fn.offset;

$.fn.position = function( options ) {
	if ( !options || !options.of ) {
		return _position.apply( this, arguments );
	}

	// make a copy, we don't want to modify arguments
	options = $.extend( {}, options );

	var target = $( options.of ),
		targetElem = target[0],
		collision = ( options.collision || "flip" ).split( " " ),
		offset = options.offset ? options.offset.split( " " ) : [ 0, 0 ],
		targetWidth,
		targetHeight,
		basePosition;

	if ( targetElem.nodeType === 9 ) {
		targetWidth = target.width();
		targetHeight = target.height();
		basePosition = { top: 0, left: 0 };
	// TODO: use $.isWindow() in 1.9
	} else if ( targetElem.setTimeout ) {
		targetWidth = target.width();
		targetHeight = target.height();
		basePosition = { top: target.scrollTop(), left: target.scrollLeft() };
	} else if ( targetElem.preventDefault ) {
		// force left top to allow flipping
		options.at = "left top";
		targetWidth = targetHeight = 0;
		basePosition = { top: options.of.pageY, left: options.of.pageX };
	} else {
		targetWidth = target.outerWidth();
		targetHeight = target.outerHeight();
		basePosition = target.offset();
	}

	// force my and at to have valid horizontal and veritcal positions
	// if a value is missing or invalid, it will be converted to center 
	$.each( [ "my", "at" ], function() {
		var pos = ( options[this] || "" ).split( " " );
		if ( pos.length === 1) {
			pos = horizontalPositions.test( pos[0] ) ?
				pos.concat( [center] ) :
				verticalPositions.test( pos[0] ) ?
					[ center ].concat( pos ) :
					[ center, center ];
		}
		pos[ 0 ] = horizontalPositions.test( pos[0] ) ? pos[ 0 ] : center;
		pos[ 1 ] = verticalPositions.test( pos[1] ) ? pos[ 1 ] : center;
		options[ this ] = pos;
	});

	// normalize collision option
	if ( collision.length === 1 ) {
		collision[ 1 ] = collision[ 0 ];
	}

	// normalize offset option
	offset[ 0 ] = parseInt( offset[0], 10 ) || 0;
	if ( offset.length === 1 ) {
		offset[ 1 ] = offset[ 0 ];
	}
	offset[ 1 ] = parseInt( offset[1], 10 ) || 0;

	if ( options.at[0] === "right" ) {
		basePosition.left += targetWidth;
	} else if ( options.at[0] === center ) {
		basePosition.left += targetWidth / 2;
	}

	if ( options.at[1] === "bottom" ) {
		basePosition.top += targetHeight;
	} else if ( options.at[1] === center ) {
		basePosition.top += targetHeight / 2;
	}

	basePosition.left += offset[ 0 ];
	basePosition.top += offset[ 1 ];

	return this.each(function() {
		var elem = $( this ),
			elemWidth = elem.outerWidth(),
			elemHeight = elem.outerHeight(),
			marginLeft = parseInt( $.curCSS( this, "marginLeft", true ) ) || 0,
			marginTop = parseInt( $.curCSS( this, "marginTop", true ) ) || 0,
			collisionWidth = elemWidth + marginLeft +
				( parseInt( $.curCSS( this, "marginRight", true ) ) || 0 ),
			collisionHeight = elemHeight + marginTop +
				( parseInt( $.curCSS( this, "marginBottom", true ) ) || 0 ),
			position = $.extend( {}, basePosition ),
			collisionPosition;

		if ( options.my[0] === "right" ) {
			position.left -= elemWidth;
		} else if ( options.my[0] === center ) {
			position.left -= elemWidth / 2;
		}

		if ( options.my[1] === "bottom" ) {
			position.top -= elemHeight;
		} else if ( options.my[1] === center ) {
			position.top -= elemHeight / 2;
		}

		// prevent fractions (see #5280)
		position.left = Math.round( position.left );
		position.top = Math.round( position.top );

		collisionPosition = {
			left: position.left - marginLeft,
			top: position.top - marginTop
		};

		$.each( [ "left", "top" ], function( i, dir ) {
			if ( $.ui.position[ collision[i] ] ) {
				$.ui.position[ collision[i] ][ dir ]( position, {
					targetWidth: targetWidth,
					targetHeight: targetHeight,
					elemWidth: elemWidth,
					elemHeight: elemHeight,
					collisionPosition: collisionPosition,
					collisionWidth: collisionWidth,
					collisionHeight: collisionHeight,
					offset: offset,
					my: options.my,
					at: options.at
				});
			}
		});

		if ( $.fn.bgiframe ) {
			elem.bgiframe();
		}
		elem.offset( $.extend( position, { using: options.using } ) );
	});
};

$.ui.position = {
	fit: {
		left: function( position, data ) {
			var win = $( window ),
				over = data.collisionPosition.left + data.collisionWidth - win.width() - win.scrollLeft();
			position.left = over > 0 ? position.left - over : Math.max( position.left - data.collisionPosition.left, position.left );
		},
		top: function( position, data ) {
			var win = $( window ),
				over = data.collisionPosition.top + data.collisionHeight - win.height() - win.scrollTop();
			position.top = over > 0 ? position.top - over : Math.max( position.top - data.collisionPosition.top, position.top );
		}
	},

	flip: {
		left: function( position, data ) {
			if ( data.at[0] === center ) {
				return;
			}
			var win = $( window ),
				over = data.collisionPosition.left + data.collisionWidth - win.width() - win.scrollLeft(),
				myOffset = data.my[ 0 ] === "left" ?
					-data.elemWidth :
					data.my[ 0 ] === "right" ?
						data.elemWidth :
						0,
				atOffset = data.at[ 0 ] === "left" ?
					data.targetWidth :
					-data.targetWidth,
				offset = -2 * data.offset[ 0 ];
			position.left += data.collisionPosition.left < 0 ?
				myOffset + atOffset + offset :
				over > 0 ?
					myOffset + atOffset + offset :
					0;
		},
		top: function( position, data ) {
			if ( data.at[1] === center ) {
				return;
			}
			var win = $( window ),
				over = data.collisionPosition.top + data.collisionHeight - win.height() - win.scrollTop(),
				myOffset = data.my[ 1 ] === "top" ?
					-data.elemHeight :
					data.my[ 1 ] === "bottom" ?
						data.elemHeight :
						0,
				atOffset = data.at[ 1 ] === "top" ?
					data.targetHeight :
					-data.targetHeight,
				offset = -2 * data.offset[ 1 ];
			position.top += data.collisionPosition.top < 0 ?
				myOffset + atOffset + offset :
				over > 0 ?
					myOffset + atOffset + offset :
					0;
		}
	}
};

// offset setter from jQuery 1.4
if ( !$.offset.setOffset ) {
	$.offset.setOffset = function( elem, options ) {
		// set position first, in-case top/left are set even on static elem
		if ( /static/.test( $.curCSS( elem, "position" ) ) ) {
			elem.style.position = "relative";
		}
		var curElem   = $( elem ),
			curOffset = curElem.offset(),
			curTop    = parseInt( $.curCSS( elem, "top",  true ), 10 ) || 0,
			curLeft   = parseInt( $.curCSS( elem, "left", true ), 10)  || 0,
			props     = {
				top:  (options.top  - curOffset.top)  + curTop,
				left: (options.left - curOffset.left) + curLeft
			};
		
		if ( 'using' in options ) {
			options.using.call( elem, props );
		} else {
			curElem.css( props );
		}
	};

	$.fn.offset = function( options ) {
		var elem = this[ 0 ];
		if ( !elem || !elem.ownerDocument ) { return null; }
		if ( options ) { 
			return this.each(function() {
				$.offset.setOffset( this, options );
			});
		}
		return _offset.call( this );
	};
}

}( jQuery ));
/*!
 * Fluid Infusion v1.5
 *
 * Infusion is distributed under the Educational Community License 2.0 and new BSD licenses: 
 * http://wiki.fluidproject.org/display/fluid/Fluid+Licensing
 *
 * For information on copyright, see the individual Infusion source code files: 
 * https://github.com/fluid-project/infusion/
 */

/*
Copyright 2007-2010 University of Cambridge
Copyright 2007-2009 University of Toronto
Copyright 2007-2009 University of California, Berkeley
Copyright 2010-2011 Lucendo Development Ltd.
Copyright 2010 OCAD University
Copyright 2011 Charly Molter

Licensed under the Educational Community License (ECL), Version 2.0 or the New
BSD license. You may not use this file except in compliance with one these
Licenses.

You may obtain a copy of the ECL 2.0 License and BSD License at
https://github.com/fluid-project/infusion/raw/master/Infusion-LICENSE.txt
*/

// Declare dependencies
/*global console, window, fluid:true, fluid_1_5:true, jQuery, opera, YAHOO*/

// JSLint options 
/*jslint white: true, funcinvoke: true, continue: true, jslintok: true, undef: true, newcap: true, nomen: true, regexp: true, bitwise: true, browser: true, forin: true, maxerr: 100, indent: 4 */

var fluid_1_5 = fluid_1_5 || {};
var fluid = fluid || fluid_1_5;

(function ($, fluid) {
    
    fluid.version = "Infusion 1.5";
    
    fluid.environment = {
        fluid: fluid
    };
    var globalObject = window || {};
    
    fluid.singleThreadLocal = function(initFunc) {
        var value = initFunc();
        return function() {
            return value;
        };
    };
    
    // Return to the old strategy of monkey-patching this, since this is a most frequently used function within IoC    
    fluid.threadLocal = fluid.singleThreadLocal;
    
    var softFailure = [false];
    
    // This function will be patched from FluidIoC.js in order to describe complex activities
    fluid.describeActivity = function () {
        return [];
    };
    
    /**
     * Causes an error message to be logged to the console and a real runtime error to be thrown.
     * 
     * @param {String|Error} message the error message to log
     * @param ... Additional arguments
     */
    fluid.fail = function (message /*, ... */) { // jslint:ok - whitespace in arg list
        fluid.setLogging(true);
        fluid.log.apply(null, ["ASSERTION FAILED: "].concat(fluid.makeArray(arguments)).concat(fluid.describeActivity()));
        if (softFailure[0]) {
            throw new Error(message);
        } else {
            message.fail(); // Intentionally cause a browser error by invoking a nonexistent function.
        }
    };
    
    fluid.pushSoftFailure = function (condition) {
        if (typeof (condition) === "boolean") {
            softFailure.unshift(condition);
        } else if (condition === -1) {
            softFailure.shift();
        }
    };
    
    fluid.notrycatch = false;
    
    // A wrapper for the try/catch/finally language feature, to aid debugging on environments
    // such as IE, where any try will destroy stack information for errors
    fluid.tryCatch = function (tryfun, catchfun, finallyfun) {
        finallyfun = finallyfun || fluid.identity;
        if (fluid.notrycatch) {
            var togo = tryfun();
            finallyfun();
            return togo;
        } else {
            try {
                return tryfun();  
            } catch (e) {
                if (catchfun) {
                    catchfun(e);
                } else { 
                    throw (e);
                }
            } finally {
                finallyfun();
            }
        }
    };
    
    // TODO: rescued from kettleCouchDB.js - clean up in time
    fluid.expect = function (name, members, target) {
        fluid.transform(fluid.makeArray(members), function (key) {
            if (typeof target[key] === "undefined") {
                fluid.fail(name + " missing required parameter " + key);
            }
        });
    };

    // Logging

    var logging;
        
    /** Returns whether logging is enabled **/
    fluid.isLogging = function () {
        return logging;
    };

    /** method to allow user to enable logging (off by default) */
    fluid.setLogging = function (enabled) {
        if (typeof enabled === "boolean") {
            logging = enabled;
        } else {
            logging = false;
        }
    };

    // On some dodgy environments (notably IE9 and recent alphas of Firebug 1.8), 
    // console.log/debug are incomplete function objects and need to be operated via
    // this trick: http://stackoverflow.com/questions/5472938/does-ie9-support-console-log-and-is-it-a-real-function
    fluid.applyHostFunction = function (obj, func, args) {
        if (func.apply) {
            func.apply(obj, args);
        } else {
            var applier = Function.prototype.bind.call(func, obj);
            applier.apply(obj, args);
        }
    };

    /** Log a message to a suitable environmental console. If the standard "console" 
     * stream is available, the message will be sent there - otherwise either the
     * YAHOO logger or the Opera "postError" stream will be used. Logging must first
     * be enabled with a call to the fluid.setLogging(true) function.
     */
    fluid.log = function (message /*, ... */) { // jslint:ok - whitespace in arg list
        if (logging) {
            var arg0 = fluid.renderTimestamp(new Date()) + ":  "; 
            var args = [arg0].concat(fluid.makeArray(arguments));
            var str = args.join("");
            if (typeof (console) !== "undefined") {
                if (console.debug) {
                    fluid.applyHostFunction(console, console.debug, args);
                } else if (typeof (console.log) === "function") {
                    fluid.applyHostFunction(console, console.log, args);
                } else {
                    console.log(str); // this branch executes on old IE, fully synthetic console.log
                }
            } else if (typeof (YAHOO) !== "undefined") {
                YAHOO.log(str);
            } else if (typeof (opera) !== "undefined") {
                opera.postError(str);
            }
        }
    };
     
    // Functional programming utilities.
               
    /** A basic utility that returns its argument unchanged */
    
    fluid.identity = function (arg) {
        return arg;
    };
    
    // Framework and instantiation functions.

    
    /** Returns true if the argument is a value other than null or undefined **/
    fluid.isValue = function (value) {
        return value !== undefined && value !== null;
    };
    
    /** Returns true if the argument is a primitive type **/
    fluid.isPrimitive = function (value) {
        var valueType = typeof (value);
        return !value || valueType === "string" || valueType === "boolean" || valueType === "number" || valueType === "function";
    };
    
    /** Determines whether the supplied object is an array. The strategy used is an optimised
     * approach taken from an earlier version of jQuery - detecting whether the toString() version
     * of the object agrees with the textual form [object Array], or else whether the object is a 
     * jQuery object (the most common source of "fake arrays").
     */
    fluid.isArrayable = function (totest) {
        return totest && (totest.jquery || Object.prototype.toString.call(totest) === "[object Array]");
    };
    
    fluid.isDOMNode = function (obj) {
      // This could be more sound, but messy: 
      // http://stackoverflow.com/questions/384286/javascript-isdom-how-do-you-check-if-a-javascript-object-is-a-dom-object
        return obj && typeof (obj.nodeType) === "number";  
    };
    
    /** Return an empty container as the same type as the argument (either an
     * array or hash */
    fluid.freshContainer = function (tocopy) {
        return fluid.isArrayable(tocopy) ? [] : {};   
    };
    
    /** Performs a deep copy (clone) of its argument **/
    
    fluid.copy = function (tocopy) {
        if (fluid.isPrimitive(tocopy)) {
            return tocopy;
        }
        return $.extend(true, fluid.freshContainer(tocopy), tocopy);
    };
            
    /** Corrected version of jQuery makeArray that returns an empty array on undefined rather than crashing.
      * We don't deal with as many pathological cases as jQuery **/
    fluid.makeArray = function (arg) {
        var togo = [];
        if (arg !== null && arg !== undefined) {
            if (fluid.isPrimitive(arg) || typeof(arg.length) !== "number") {
                togo.push(arg); 
            }
            else {
                for (var i = 0; i < arg.length; ++ i) {
                    togo[i] = arg[i];
                }
            }
        }
        return togo;
    };
    
    function transformInternal(source, togo, key, args) {
        var transit = source[key];
        for (var j = 0; j < args.length - 1; ++j) {
            transit = args[j + 1](transit, key);
        }
        togo[key] = transit; 
    }
    
    /** Return a list or hash of objects, transformed by one or more functions. Similar to
     * jQuery.map, only will accept an arbitrary list of transformation functions and also
     * works on non-arrays.
     * @param source {Array or Object} The initial container of objects to be transformed.
     * @param fn1, fn2, etc. {Function} An arbitrary number of optional further arguments,
     * all of type Function, accepting the signature (object, index), where object is the
     * list member to be transformed, and index is its list index. Each function will be
     * applied in turn to each list member, which will be replaced by the return value
     * from the function.
     * @return The finally transformed list, where each member has been replaced by the
     * original member acted on by the function or functions.
     */
    fluid.transform = function (source) {
        var togo = fluid.freshContainer(source);
        if (fluid.isArrayable(source)) {
            for (var i = 0; i < source.length; ++i) {
                transformInternal(source, togo, i, arguments);
            }
        } else {
            for (var key in source) {
                transformInternal(source, togo, key, arguments);
            }
        }  
        return togo;
    };
    
    /** Better jQuery.each which works on hashes as well as having the arguments
     * the right way round. 
     * @param source {Arrayable or Object} The container to be iterated over
     * @param func {Function} A function accepting (value, key) for each iterated
     * object. This function may return a value to terminate the iteration
     */
    fluid.each = function (source, func) {
        if (fluid.isArrayable(source)) {
            for (var i = 0; i < source.length; ++i) {
                func(source[i], i);
            }
        } else {
            for (var key in source) {
                func(source[key], key);
            }
        }
    };
    
    /** Scan through a list or hash of objects, terminating on the first member which
     * matches a predicate function.
     * @param source {Arrayable or Object} The list or hash of objects to be searched.
     * @param func {Function} A predicate function, acting on a member. A predicate which
     * returns any value which is not <code>undefined</code> will terminate
     * the search. The function accepts (object, index).
     * @param deflt {Object} A value to be returned in the case no predicate function matches
     * a list member. The default will be the natural value of <code>undefined</code>
     * @return The first return value from the predicate function which is not <code>undefined</code>
     */
    fluid.find = function (source, func, deflt) {
        var disp;
        if (fluid.isArrayable(source)) {
            for (var i = 0; i < source.length; ++i) {
                disp = func(source[i], i);
                if (disp !== undefined) {
                    return disp;
                }
            }
        } else {
            for (var key in source) {
                disp = func(source[key], key);
                if (disp !== undefined) {
                    return disp;
                }
            }
        }
        return deflt;
    };
    
    /** Scan through a list of objects, "accumulating" a value over them 
     * (may be a straightforward "sum" or some other chained computation).
     * @param list {Array} The list of objects to be accumulated over.
     * @param fn {Function} An "accumulation function" accepting the signature (object, total, index) where
     * object is the list member, total is the "running total" object (which is the return value from the previous function),
     * and index is the index number.
     * @param arg {Object} The initial value for the "running total" object.
     * @return {Object} the final running total object as returned from the final invocation of the function on the last list member.
     */
    fluid.accumulate = function (list, fn, arg) {
        for (var i = 0; i < list.length; ++i) {
            arg = fn(list[i], arg, i);
        }
        return arg;
    };
    
    /** Can through a list of objects, removing those which match a predicate. Similar to
     * jQuery.grep, only acts on the list in-place by removal, rather than by creating
     * a new list by inclusion.
     * @param source {Array|Object} The list of objects to be scanned over.
     * @param fn {Function} A predicate function determining whether an element should be
     * removed. This accepts the standard signature (object, index) and returns a "truthy"
     * result in order to determine that the supplied object should be removed from the list.
     * @return The list, transformed by the operation of removing the matched elements. The
     * supplied list is modified by this operation.
     */
    fluid.remove_if = function (source, fn) {
        if (fluid.isArrayable(source)) {
            for (var i = 0; i < source.length; ++i) {
                if (fn(source[i], i)) {
                    source.splice(i, 1);
                    --i;
                }
            }
        } else {
            for (var key in source) {
                if (fn(source[key], key)) {
                    delete source[key];
                }
            }
        }
        return source;
    };
    
    /** Accepts an object to be filtered, and a list of keys. Either all keys not present in
     * the list are removed, or only keys present in the list are returned.
     * @param toFilter {Array|Object} The object to be filtered - this will be modified by the operation
     * @param keys {Array of String} The list of keys to operate with
     * @param exclude {boolean} If <code>true</code>, the keys listed are removed rather than included
     * @return the filtered object (the same object that was supplied as <code>toFilter</code>
     */
    
    fluid.filterKeys = function (toFilter, keys, exclude) {
        return fluid.remove_if($.extend({}, toFilter), function (value, key) {
            return exclude ^ ($.inArray(key, keys) === -1);
        });
    };
    
    /** A convenience wrapper for <code>fluid.filterKeys</code> with the parameter <code>exclude</code> set to <code>true</code>
     *  Returns the supplied object with listed keys removed */

    fluid.censorKeys = function (toCensor, keys) {
        return fluid.filterKeys(toCensor, keys, true);
    };
    
    /** Return the keys in the supplied object as an array **/
    fluid.keys = function (obj) {
        var togo = [];
        fluid.each(obj, function (value, key) {
            togo.push(key);
        });
        return togo;
    };
    
    /** 
     * Searches through the supplied object, and returns <code>true</code> if the supplied value
     * can be found 
     */
    fluid.contains = function (obj, value) {
        return obj ? fluid.find(obj, function (thisValue, key) {
            if (value === thisValue) {
                return true;
            }
        }) : undefined;
    };
    
    /** 
     * Searches through the supplied object for the first value which matches the one supplied.
     * @param obj {Object} the Object to be searched through
     * @param value {Object} the value to be found. This will be compared against the object's
     * member using === equality.
     * @return {String} The first key whose value matches the one supplied, or <code>null</code> if no
     * such key is found.
     */
    fluid.keyForValue = function (obj, value) {
        return fluid.find(obj, function (thisValue, key) {
            if (value === thisValue) {
                return key;
            }
        });
    };
    
    /**
     * This method is now deprecated and will be removed in a future release of Infusion. 
     * See fluid.keyForValue instead.
     */
    fluid.findKeyInObject = fluid.keyForValue;
    
    /** Converts an array into an object whose keys are the elements of the array, each with the value "true"
     */ 
    
    fluid.arrayToHash = function (array) {
        var togo = {};
        fluid.each(array, function (el) {
            togo[el] = true;
        });
        return togo;
    };
    
    /** 
     * Clears an object or array of its contents. For objects, each property is deleted.
     * 
     * @param {Object|Array} target the target to be cleared
     */
    fluid.clear = function (target) {
        if (fluid.isArrayable(target)) {
            target.length = 0;
        } else {
            for (var i in target) {
                delete target[i];
            }
        }
    };
    
   /**
    * @param boolean ascending <code>true</code> if a comparator is to be returned which 
    * sorts strings in descending order of length
    */
    fluid.compareStringLength = function (ascending) {
        return ascending ? function (a, b) {
            return a.length - b.length;
        } : function (a, b) {
            return b.length - a.length;
        };
    };
        
    // Model functions
    fluid.model = {}; // cannot call registerNamespace yet since it depends on fluid.model
       
    /** Another special "marker object" representing that a distinguished 
     * (probably context-dependent) value should be substituted.
     */
    fluid.VALUE = {type: "fluid.marker", value: "VALUE"};
    
    /** Another special "marker object" representing that no value is present (where
     * signalling using the value "undefined" is not possible) */
    fluid.NO_VALUE = {type: "fluid.marker", value: "NO_VALUE"};
    
    /** A marker indicating that a value requires to be expanded after component construction begins **/
    fluid.EXPAND = {type: "fluid.marker", value: "EXPAND"};
    /** A marker indicating that a value requires to be expanded immediately**/
    fluid.EXPAND_NOW = {type: "fluid.marker", value: "EXPAND_NOW"};
    
    /** Determine whether an object is any marker, or a particular marker - omit the
     * 2nd argument to detect any marker
     */
    fluid.isMarker = function (totest, type) {
        if (!totest || typeof (totest) !== 'object' || totest.type !== "fluid.marker") {
            return false;
        }
        if (!type) {
            return true;
        }
        return totest === type;
    };
   
    /** Copy a source "model" onto a target **/
    fluid.model.copyModel = function (target, source) {
        fluid.clear(target);
        $.extend(true, target, source);
    };
    
    /** Parse an EL expression separated by periods (.) into its component segments.
     * @param {String} EL The EL expression to be split
     * @return {Array of String} the component path expressions.
     * TODO: This needs to be upgraded to handle (the same) escaping rules (as RSF), so that
     * path segments containing periods and backslashes etc. can be processed, and be harmonised
     * with the more complex implementations in fluid.pathUtil(data binding).
     */
    fluid.model.parseEL = function (EL) {
        return EL === "" ? [] : String(EL).split('.');
    };
    
    /** Compose an EL expression from two separate EL expressions. The returned 
     * expression will be the one that will navigate the first expression, and then
     * the second, from the value reached by the first. Either prefix or suffix may be
     * the empty string **/
    
    fluid.model.composePath = function (prefix, suffix) {
        return prefix === "" ? suffix : (suffix === "" ? prefix : prefix + "." + suffix);
    };
    
    /** Compose any number of path segments, none of which may be empty **/
    fluid.model.composeSegments = function () {
        return fluid.makeArray(arguments).join(".");
    };
    
    /** Helpful alias for old-style API **/
    fluid.path = fluid.model.composeSegments;
    fluid.composePath = fluid.model.composePath;


    // unsupported, NON-API function
    fluid.requireDataBinding = function () {
        fluid.fail("Please include DataBinding.js in order to operate complex model accessor configuration");  
    };
    
    fluid.model.trundle = fluid.model.getPenultimate = fluid.requireDataBinding;
    
    // unsupported, NON-API function
    fluid.model.resolvePathSegment = function (root, segment, create, origEnv) {
        if (!origEnv && root.resolvePathSegment) {
            return root.resolvePathSegment(segment);
        }
        if (create && root[segment] === undefined) {
            // This optimisation in this heavily used function has a fair effect
            return root[segment] = {};
        }
        return root[segment];
    };
    
    // unsupported, NON-API function
    fluid.model.getPenultimateSimple = function (root, EL, environment, create) {
        var origEnv = environment;
        var segs = fluid.model.parseEL(EL);
        for (var i = 0; i < segs.length - 1; ++i) {
            if (!root) {
                return {root: root };
            }
            var segment = segs[i];
            if (environment && environment[segment]) {
                root = environment[segment];
                environment = null;
            } else {
                root = fluid.model.resolvePathSegment(root, segment, create, origEnv);
            }
        }
        return {root: root, last: segs[segs.length - 1]};
    };
    
    fluid.model.setSimple = function (root, EL, newValue, environment) {
        var pen = fluid.model.getPenultimateSimple(root, EL, environment, true);
        pen.root[pen.last] = newValue;
    };
    
    /** Evaluates an EL expression by fetching a dot-separated list of members
     * recursively from a provided root.
     * @param root The root data structure in which the EL expression is to be evaluated
     * @param {string} EL The EL expression to be evaluated
     * @param environment An optional "environment" which, if it contains any members
     * at top level, will take priority over the root data structure.
     * @return The fetched data value.
     */
    
    fluid.model.getSimple = function (root, EL, environment) {
        if (EL === "" || EL === null || EL === undefined) {
            return root;
        }
        var pen = fluid.model.getPenultimateSimple(root, EL, environment);
        return pen.root ? pen.root[pen.last] : pen.root;
    };
    
    // unsupported, NON-API function
    // Returns undefined to signal complex configuration which needs to be farmed out to DataBinding.js
    // any other return represents an environment value AND a simple configuration we can handle here
    fluid.decodeAccessorArg = function (arg3) {
        return (!arg3 || arg3 === fluid.model.defaultGetConfig || arg3 === fluid.model.defaultSetConfig) ? 
            null : (arg3.type === "environment" ? arg3.value : undefined);
    };
    
    fluid.set = function (root, EL, newValue, config) {
        var env = fluid.decodeAccessorArg(config);
        if (env === undefined) {
            var trundler = fluid.model.getPenultimate(root, EL, config);
            trundler.root[trundler.last] = newValue;
        } else {
            fluid.model.setSimple(root, EL, newValue, env);
        }
    };
    
    /** Evaluates an EL expression by fetching a dot-separated list of members
     * recursively from a provided root.
     * @param root The root data structure in which the EL expression is to be evaluated
     * @param {string} EL The EL expression to be evaluated
     * @param environment An optional "environment" which, if it contains any members
     * at top level, will take priority over the root data structure.
     * @return The fetched data value.
     */
    
    fluid.get = function (root, EL, config) {
        var env = fluid.decodeAccessorArg(config);
        return env === undefined ? 
            fluid.model.trundle(root, EL, config).root 
            : fluid.model.getSimple(root, EL, env);
    };

    // This backward compatibility will be maintained for a number of releases, probably until Fluid 2.0
    fluid.model.setBeanValue = fluid.set;
    fluid.model.getBeanValue = fluid.get;
    
    fluid.getGlobalValue = function (path, env) {
        if (path) {
            env = env || fluid.environment;
            return fluid.get(globalObject, path, {type: "environment", value: env});
        }
    };
    
    /**
     * Allows for the calling of a function from an EL expression "functionPath", with the arguments "args", scoped to an framework version "environment".
     * @param {Object} functionPath - An EL expression
     * @param {Object} args - An array of arguments to be applied to the function, specified in functionPath
     * @param {Object} environment - (optional) The object to scope the functionPath to  (typically the framework root for version control)
     */
    fluid.invokeGlobalFunction = function (functionPath, args, environment) {
        var func = fluid.getGlobalValue(functionPath, environment);
        if (!func) {
            fluid.fail("Error invoking global function: " + functionPath + " could not be located");
        } else {
            return func.apply(null, args);
        }
    };
    
    /** Registers a new global function at a given path (currently assumes that
     * it lies within the fluid namespace)
     */
    
    fluid.registerGlobalFunction = function (functionPath, func, env) {
        env = env || fluid.environment;
        fluid.set(globalObject, functionPath, func, {type: "environment", value: env});
    };
    
    fluid.setGlobalValue = fluid.registerGlobalFunction;
    
    /** Ensures that an entry in the global namespace exists **/
    fluid.registerNamespace = function (naimspace, env) {
        env = env || fluid.environment;
        var existing = fluid.getGlobalValue(naimspace, env);
        if (!existing) {
            existing = {};
            fluid.setGlobalValue(naimspace, existing, env);
        }
        return existing;
    };
    
    // stubs for two functions in FluidDebugging.js
    fluid.dumpEl = fluid.identity;
    fluid.renderTimestamp = fluid.identity;
    
    
    /*** The Model Events system. ***/
    
    fluid.registerNamespace("fluid.event");
    
    fluid.generateUniquePrefix = function () {
        return (Math.floor(Math.random() * 1e12)).toString(36) + "-";
    };
    
    var fluid_prefix = fluid.generateUniquePrefix(); 
    
    var fluid_guid = 1;
    
    /** Allocate an string value that will be very likely unique within this (browser) process **/
    
    fluid.allocateGuid = function () {
        return fluid_prefix + (fluid_guid++);
    };
    
    fluid.event.identifyListener = function (listener) {
        if (typeof (listener) === "string") {
            return listener; 
        }
        if (!listener.$$guid) {
            listener.$$guid = fluid.allocateGuid();
        }
        return listener.$$guid;
    };
    
    // unsupported, NON-API function
    fluid.event.mapPriority = function (priority, count) {
        return (priority === null || priority === undefined ? -count : 
           (priority === "last" ? -Number.MAX_VALUE :
              (priority === "first" ? Number.MAX_VALUE : priority)));
    };
    
    // unsupported, NON-API function
    fluid.event.listenerComparator = function (recA, recB) {
        return recB.priority - recA.priority;
    };
    
    // unsupported, NON-API function
    fluid.event.sortListeners = function (listeners) {
        var togo = [];
        fluid.each(listeners, function (listener) {
            togo.push(listener);
        });
        return togo.sort(fluid.event.listenerComparator);
    };
    
    // unsupported, NON-API function
    fluid.event.resolveListener = function (listener) {
        if (typeof (listener) === "string") {
            var listenerFunc = fluid.getGlobalValue(listener);
            if (!listenerFunc) {
                fluid.fail("Unable to look up name " + listener + " as a global function"); 
            } else {
                listener = listenerFunc;
            }
        }
        return listener;
    };
    
    fluid.event.nameEvent = function (that, eventName) {
        return eventName + " of " + fluid.nameComponent(that);
    };
    
    /** Construct an "event firer" object which can be used to register and deregister 
     * listeners, to which "events" can be fired. These events consist of an arbitrary
     * function signature. General documentation on the Fluid events system is at
     * http://wiki.fluidproject.org/display/fluid/The+Fluid+Event+System .
     * @param {Boolean} unicast If <code>true</code>, this is a "unicast" event which may only accept
     * a single listener.
     * @param {Boolean} preventable If <code>true</code> the return value of each handler will 
     * be checked for <code>false</code> in which case further listeners will be shortcircuited, and this
     * will be the return value of fire()
     */
    // This name will be deprecated in Fluid 2.0 for fluid.makeEventFirer (or fluid.eventFirer)
    fluid.event.getEventFirer = function (unicast, preventable, name) {
        var listeners = {};
        var sortedListeners = [];
        
        function fireToListeners(listeners, args, wrapper) {
            fluid.log("Firing event " + name + " to list of " + listeners.length + " listeners");
            for (var i = 0; i < listeners.length; ++i) {
                var lisrec = listeners[i];
                lisrec.listener = fluid.event.resolveListener(lisrec.listener);
                var listener = lisrec.listener;

                if (lisrec.predicate && !lisrec.predicate(listener, args)) {
                    continue;
                }
                var value = fluid.tryCatch(function () {
                    var ret = (wrapper ? wrapper(listener) : listener).apply(null, args);
                    if (preventable && ret === false) {
                        return false;
                    }
                    if (unicast) {
                        return ret;
                    }
                }, function (e) { // jslint:ok - function within a loop, only invoked synchronously
                    fluid.log("FireEvent received exception " + e.message + " e " + e + " firing to listener " + i);
                    throw (e);       
                }); // jslint:ok - function within loop
                if (value !== undefined) {
                    return value;
                }
            }
        }
        
        return {
            name: name,
            typeName: "fluid.event.firer", 
            addListener: function (listener, namespace, predicate, priority) {
                if (!listener) {
                    return;
                }
                if (unicast) {
                    namespace = "unicast";
                }
                if (!namespace) {
                    namespace = fluid.event.identifyListener(listener);
                }

                listeners[namespace] = {listener: listener, predicate: predicate, priority: 
                    fluid.event.mapPriority(priority, sortedListeners.length)};
                sortedListeners = fluid.event.sortListeners(listeners);
            },

            removeListener: function (listener) {
                if (typeof (listener) === 'string') {
                    delete listeners[listener];
                } else if (listener.$$guid) {
                    delete listeners[listener.$$guid];
                }
                sortedListeners = fluid.event.sortListeners(listeners);
            },
            // NB - this method exists currently solely for the convenience of the new,
            // transactional changeApplier. As it exists it is hard to imagine the function
            // being helpful to any other client. We need to get more experience on the kinds
            // of listeners that are useful, and ultimately factor this method away.
            fireToListeners: function (listeners, args, wrapper) {
                return fireToListeners(listeners, args, wrapper);
            },
            fire: function () {
                return fireToListeners(sortedListeners, arguments);
            }
        };
    };
    
    fluid.makeEventFirer = fluid.event.getEventFirer;
    
    /** Fire the specified event with supplied arguments. This call is an optimisation utility
     * which handles the case where the firer has not been instantiated (presumably as a result
     * of having no listeners registered 
     */
     
    fluid.fireEvent = function (firer, args) {
        if (firer) {
            firer.fire.apply(null, fluid.makeArray(args));
        }  
    };
    
    // unsupported, NON-API function
    fluid.event.addListenerToFirer = function (firer, value, namespace) {
        if (fluid.isArrayable(value)) {
            for (var i = 0; i < value.length; ++i) {
                fluid.event.addListenerToFirer(firer, value[i], namespace); 
            }
        } else if (typeof (value) === "function" || typeof (value) === "string") {
            firer.addListener(value, namespace);
        } else if (value && typeof (value) === "object") {
            firer.addListener(value.listener, namespace || value.namespace, value.predicate, value.priority);
        }
    };
    
    fluid.event.resolveListenerRecord = fluid.identity; // non-IOC passthrough
    
    // unsupported, NON-API function
    fluid.mergeListeners = function (that, events, listeners) {
        fluid.each(listeners, function (value, key) {
            var firer, namespace;
            if (key.charAt(0) === "{") {
                if (!fluid.expandOptions) {
                    fluid.fail("fluid.expandOptions could not be loaded - please include FluidIoC.js in order to operate IoC-driven event with descriptor " + 
                        key);
                }
                firer = fluid.expandOptions(key, that);
            } else {
                var keydot = key.indexOf(".");
            
                if (keydot !== -1) {
                    namespace = key.substring(keydot + 1);
                    key = key.substring(0, keydot);
                }
                if (!events[key]) {
                    fluid.fail("Listener registered for event " + key + " which is not defined for this component");
                    events[key] = fluid.makeEventFirer(null, null, fluid.event.nameEvent(that, key));
                }
                firer = events[key];
            }
            value = fluid.event.resolveListenerRecord(value, that, key);
            fluid.event.addListenerToFirer(firer, value, namespace);
        });
    };
    
    function initEvents(that, events, pass) {
        fluid.each(events, function (eventSpec, eventKey) { 
            var isIoCEvent = eventSpec && (typeof (eventSpec) !== "string" || eventSpec.charAt(0) === "{");
            var event;
            if (isIoCEvent && pass === "IoC") {
                if (!fluid.event.resolveEvent) {
                    fluid.fail("fluid.event.resolveEvent could not be loaded - please include FluidIoC.js in order to operate IoC-driven event with descriptor ", 
                        eventSpec);
                } else {
                    event = fluid.event.resolveEvent(that, eventKey, eventSpec);
                }
            } else if (pass === "flat") {
                event = fluid.makeEventFirer(eventSpec === "unicast", eventSpec === "preventable", fluid.event.nameEvent(that, eventKey));
            }
            if (event) {
                that.events[eventKey] = event;
            } 
        });
    }
    
    // unsupported, NON-API function
    fluid.instantiateFirers = function (that, options) {
        that.events = {};
        // TODO: manual 2-phase instantiation since we have no GINGER WORLD
        initEvents(that, options.events, "flat"); 
        initEvents(that, options.events, "IoC");
        // TODO: manually expand these late so that members attached to ourselves with preInitFunction can be detected
        //var listeners = fluid.expandOptions ? fluid.expandOptions(options.listeners, that) : options.listeners;
        fluid.mergeListeners(that, that.events, options.listeners);
    };
    
    fluid.mergeListenerPolicy = function (target, source, key) {
        // cf. triage in mergeListeners
        var hasNamespace = key.charAt(0) !== "{" && key.indexOf(".") !== -1; 
        return hasNamespace ? (source ? source : target) 
            : fluid.makeArray(target).concat(fluid.makeArray(source));
    };
    
    fluid.mergeListenersPolicy = function (target, source) {
        target = target || {};
        fluid.each(source, function (listeners, key) {
            target[key] = fluid.mergeListenerPolicy(target[key], listeners, key);
        });
        return target;
    };
    
    /*** DEFAULTS AND OPTIONS MERGING SYSTEM ***/
    
    var defaultsStore = {};
        
    var resolveGradesImpl = function (gs, gradeNames) {
        gradeNames = fluid.makeArray(gradeNames);
        fluid.each(gradeNames, function (gradeName) {
            var options = fluid.rawDefaults(gradeName) || {};
            gs.gradeHash[gradeName] = true;
            gs.gradeChain.push(gradeName);
            gs.optionsChain.push(options);
            fluid.each(options.gradeNames, function (parent) {
                if (!gs.gradeHash[parent]) {
                    resolveGradesImpl(gs, parent);
                }
            });
        });
        return gs;
    };
    
    // unsupported, NON-API function
    fluid.resolveGradeStructure = function (gradeNames) {
        var gradeStruct = {
            gradeChain: [],
            gradeHash: {},
            optionsChain: []
        };
        return resolveGradesImpl(gradeStruct, gradeNames);
    };
    
    fluid.lifecycleFunctions = {
        preInitFunction: true,
        postInitFunction: true,
        finalInitFunction: true
    };
    
    fluid.rootMergePolicy = fluid.transform(fluid.lifecycleFunctions, function () {
        return fluid.mergeListenerPolicy;
    });
    
    var mergedDefaultsCache = {};
    
    fluid.gradeNamesToKey = function (gradeNames, defaultName) {
        return defaultName + "|" + fluid.makeArray(gradeNames).sort().join("|");
    };
    
    // unsupported, NON-API function
    fluid.resolveGrade = function (defaults, defaultName, gradeNames) {
        var mergeArgs = [defaults];
        if (gradeNames) {
            var gradeStruct = fluid.resolveGradeStructure(gradeNames);
            mergeArgs = gradeStruct.optionsChain.reverse().concat(mergeArgs).concat({gradeNames: gradeStruct.gradeChain});
        }
        mergeArgs = [fluid.rootMergePolicy, {}].concat(mergeArgs);
        var mergedDefaults = fluid.merge.apply(null, mergeArgs);
        return mergedDefaults;  
    };
    
    fluid.getGradedDefaults = function (defaults, defaultName, gradeNames) {
        var key = fluid.gradeNamesToKey(gradeNames, defaultName);
        var mergedDefaults = mergedDefaultsCache[key];
        if (!mergedDefaults) {
            mergedDefaults = mergedDefaultsCache[key] = fluid.resolveGrade(defaults, defaultName, gradeNames);
        }
        return mergedDefaults;
    };

    // unsupported, NON-API function
    fluid.resolveGradedOptions = function (componentName) {
        var defaults = fluid.rawDefaults(componentName);
        if (!defaults) {
            return defaults;
        } else {
            return fluid.getGradedDefaults(defaults, componentName, defaults.gradeNames);
        }
    };
    
    // unsupported, NON-API function
    fluid.rawDefaults = function (componentName, options) {
        if (options === undefined) {
            return defaultsStore[componentName];
        } else {
            defaultsStore[componentName] = options;
        }
    };
    
        
    fluid.hasGrade = function (options, gradeName) {
        return !options || !options.gradeNames ? false : fluid.contains(options.gradeNames, gradeName);
    };
    
     /**
     * Retrieves and stores a component's default settings centrally.
     * @param {boolean} (options) if true, manipulate a global option (for the head
     *   component) rather than instance options. NB - the use of "global options" 
     *   is deprecated and will be removed from the framework in release 1.5 
     * @param {String} componentName the name of the component
     * @param {Object} (optional) an container of key/value pairs to set
     */
     
    fluid.defaults = function () {
        var offset = 0;
        if (typeof arguments[0] === "boolean") {
            offset = 1;
        }
        var componentName = (offset === 0 ? "" : "*.global-") + arguments[offset];
        var options = arguments[offset + 1];
        if (options === undefined) {
            return fluid.resolveGradedOptions(componentName);
        } else {
            if (options && options.options) {
                fluid.fail("Probable error in options structure with option named \"options\" - perhaps you meant to write these options at top level in fluid.defaults?");  
            }
            fluid.rawDefaults(componentName, options);
            if (fluid.hasGrade(options, "autoInit")) {
                fluid.makeComponent(componentName, fluid.resolveGradedOptions(componentName));
            }
        }
    };
    
    fluid.makeComponent = function (componentName, options) {
        if (!options.initFunction || !options.gradeNames) {
            fluid.fail("Cannot autoInit component " + componentName + " which does not have an initFunction and gradeName defined");
        }
        var creator = function () {
            return fluid.initComponent(componentName, arguments);
        };
        var existing = fluid.getGlobalValue(componentName);
        if (existing) {
            $.extend(creator, existing);
        }
        fluid.setGlobalValue(componentName, creator);
    };
        
    fluid.makeComponents = function (components, env) {
        fluid.each(components, function (value, key) {
            var options = {
                gradeNames: fluid.makeArray(value).concat(["autoInit"])
            };
            fluid.defaults(key, options);
        });
    };
    
    // The base system grade definitions
    
    fluid.defaults("fluid.littleComponent", {
        initFunction: "fluid.initLittleComponent",
        argumentMap: {
            options: 0
        }
    });
    
    fluid.defaults("fluid.eventedComponent", {
        gradeNames: ["fluid.littleComponent"],
        mergePolicy: {
            listeners: fluid.mergeListenersPolicy
        }
    });
    
        
    fluid.preInitModelComponent = function (that) {
        that.model = that.options.model || {};
        that.applier = that.options.applier || (fluid.makeChangeApplier ? fluid.makeChangeApplier(that.model, that.options.changeApplierOptions) : null);
    };
    
    fluid.defaults("fluid.modelComponent", {
        gradeNames: ["fluid.littleComponent"],
        preInitFunction: {
            namespace: "preInitModelComponent",
            listener: "fluid.preInitModelComponent"
        },
        mergePolicy: {
            model: "preserve",
            applier: "nomerge"
        }
    });

    /** Generate a name for a component for debugging purposes */    
    fluid.nameComponent = function (that) {
        return that ? "component with typename " + that.typeName + " and id " + that.id : "[unknown component]";
    };
    
    // unsupported, NON-API function
    fluid.guardCircularity = function (seenIds, source, message1, message2) {
        if (source && source.id) {
            if (!seenIds[source.id]) {
                seenIds[source.id] = source;
            } else if (seenIds[source.id] === source) {
                fluid.fail("Circularity in options " + message1 + " - " + fluid.nameComponent(source)
                    + " has already been seen" + message2);  
            }
        }      
    };
                
    fluid.mergePolicyIs = function (policy, test) {
        return typeof (policy) === "string" && $.inArray(test, policy.split(/\s*,\s*/)) !== -1;
    };

    // Cheapskate implementation which avoids dependency on DataBinding.js    
    fluid.model.mergeModel = function (target, source, applier) {
        if (!fluid.isPrimitive(target)) {
            var copySource = fluid.copy(source);
            $.extend(true, source, target);
            $.extend(true, source, copySource);
        }
        return source; 
    };

    function mergeImpl(policy, basePath, target, source, thisPolicy, rec) {
        if (fluid.isTracing) {
            fluid.tracing.pathCount.push(basePath);
        }
        if (fluid.mergePolicyIs(thisPolicy, "replace")) {
            fluid.clear(target);
        }
        fluid.guardCircularity(rec.seenIds, source, "merging", " when evaluating path " + basePath + " - please protect components from merging using the \"nomerge\" merge policy");
      
        for (var name in source) {
            var path = (basePath ? basePath + "." : "") + name;
            var newPolicy = policy && typeof (policy) !== "string" ? policy[path] : policy;
            var funcPolicy = typeof (newPolicy) === "function";
            var thisTarget = target[name];
            var thisSource = source[name];
            var primitiveTarget = fluid.isPrimitive(thisTarget);
    
            if (thisSource !== undefined) {
                if (!funcPolicy && thisSource !== null && typeof (thisSource) === "object" &&
                        !fluid.isDOMNode(thisSource) && !thisSource.jquery && thisSource !== fluid.VALUE &&
                        !fluid.mergePolicyIs(newPolicy, "preserve") && !fluid.mergePolicyIs(newPolicy, "nomerge") && !fluid.mergePolicyIs(newPolicy, "noexpand")) {
                    if (primitiveTarget) {
                        target[name] = thisTarget = fluid.freshContainer(thisSource);
                    }
                    mergeImpl(policy, path, thisTarget, thisSource, newPolicy, rec);
                } else {
                    if (funcPolicy) {
                        target[name] = newPolicy.call(null, thisTarget, thisSource, name);
                    } else if (!fluid.isValue(thisTarget) || !fluid.mergePolicyIs(newPolicy, "reverse")) {
                        // TODO: When "grades" are implemented, grandfather in any paired applier to perform these operations
                        // NB: mergePolicy of "preserve" now creates dependency on DataBinding.js
                        target[name] = fluid.isValue(thisTarget) && fluid.mergePolicyIs(newPolicy, "preserve") ? fluid.model.mergeModel(thisTarget, thisSource) : thisSource;
                    }
                }
            }
        }
        return target;
    }
    
    /** Merge a collection of options structures onto a target, following an optional policy.
     * This function is typically called automatically, as a result of an invocation of
     * <code>fluid.initLittleComponent</code>. The behaviour of this function is explained more fully on
     * the page http://wiki.fluidproject.org/display/fluid/Options+Merging+for+Fluid+Components .
     * @param policy {Object/String} A "policy object" specifiying the type of merge to be performed.
     * If policy is of type {String} it should take on the value "reverse" or "replace" representing
     * a static policy. If it is an
     * Object, it should contain a mapping of EL paths onto these String values, representing a
     * fine-grained policy. If it is an Object, the values may also themselves be EL paths 
     * representing that a default value is to be taken from that path.
     * @param target {Object} The options structure which is to be modified by receiving the merge results.
     * @param options1, options2, .... {Object} an arbitrary list of options structure which are to
     * be merged "on top of" the <code>target</code>. These will not be modified.    
     */
    
    fluid.merge = function (policy, target) {
        var path = "";
        
        for (var i = 2; i < arguments.length; ++i) {
            var source = arguments[i];
            if (source !== null && source !== undefined) {
                mergeImpl(policy, path, target, source, policy ? policy[""] : null, {seenIds: {}});
            }
        }
        if (policy && typeof (policy) !== "string") {
            for (var key in policy) {
                var elrh = policy[key];
                if (typeof (elrh) === "string" && elrh !== "replace" && elrh !== "preserve") {
                    var oldValue = fluid.get(target, key);
                    if (oldValue === null || oldValue === undefined) {
                        var value = fluid.get(target, elrh);
                        fluid.set(target, key, value);
                    }
                }
            }
        }
        return target;     
    };

    // unsupported, NON-API function
    fluid.transformOptions = function (mergeArgs, transRec) {
        fluid.expect("Options transformation record", ["transformer", "config"], transRec);
        var transFunc = fluid.getGlobalValue(transRec.transformer);
        var togo = fluid.transform(mergeArgs, function (value, key) {
            return key === 0 ? value : transFunc.call(null, value, transRec.config);
        });
        return togo;
    };
    
    // unsupporter, NON-API function
    fluid.lastTransformationRecord = function (extraArgs) {
        for (var i = extraArgs.length - 1; i >= 0; --i) {
            if (extraArgs[i] && extraArgs[i].transformOptions) {
                return extraArgs[i].transformOptions;
            } 
        }
    };

    /**
     * Merges the component's declared defaults, as obtained from fluid.defaults(),
     * with the user's specified overrides.
     * 
     * @param {Object} that the instance to attach the options to
     * @param {String} componentName the unique "name" of the component, which will be used
     * to fetch the default options from store. By recommendation, this should be the global
     * name of the component's creator function.
     * @param {Object} userOptions the user-specified configuration options for this component
     */
    // unsupported, NON-API function
    fluid.mergeComponentOptions = function (that, componentName, userOptions, localOptions) {
        var defaults = fluid.defaults(componentName) || {};
        var mergePolicy = $.extend({}, fluid.rootMergePolicy, defaults.mergePolicy);
        var defaultGrades = defaults.gradeNames;

        localOptions = defaultGrades ? {} : fluid.copy(fluid.getGradedDefaults({}, "", localOptions.gradeNames));
        var mergeArgs = [mergePolicy, localOptions];
        
        var extraArgs;
        if (fluid.expandComponentOptions) {
            extraArgs = fluid.expandComponentOptions(defaults, userOptions, that);
        } else {
            extraArgs = [defaults, userOptions];
        }
        var transRec = fluid.lastTransformationRecord(extraArgs);
        if (transRec) {
            extraArgs = fluid.transformOptions(extraArgs, transRec);
        }
        mergeArgs = mergeArgs.concat(extraArgs);
        that.options = fluid.merge.apply(null, mergeArgs);
    };
    
    // The Fluid Component System proper   
            
    /** A special "marker object" which is recognised as one of the arguments to 
     * fluid.initSubcomponents. This object is recognised by reference equality - 
     * where it is found, it is replaced in the actual argument position supplied
     * to the specific subcomponent instance, with the particular options block
     * for that instance attached to the overall "that" object.
     * NOTE: The use of this marker has been deprecated as of the Fluid 1.4 release in 
     * favour of the contextual EL path "{options}" - it will be removed in a future
     * release of the framework.
     */
    fluid.COMPONENT_OPTIONS = {type: "fluid.marker", value: "COMPONENT_OPTIONS"};
    
    /** Construct a dummy or "placeholder" subcomponent, that optionally provides empty
     * implementations for a set of methods.
     */
    fluid.emptySubcomponent = function (options) {
        var that = {};
        options = $.makeArray(options);
        var empty = function () {};
        for (var i = 0; i < options.length; ++i) {
            that[options[i]] = empty;
        }
        return that;
    };
    
    /** Compute a "nickname" given a fully qualified typename, by returning the last path
     * segment.
     */
    
    fluid.computeNickName = function (typeName) {
        var segs = fluid.model.parseEL(typeName);
        return segs[segs.length - 1];
    };
        
    /** Create a "type tag" component with no state but simply a type name and id. The most 
     *  minimal form of Fluid component */
       
    fluid.typeTag = function (name) {
        return name ? {
            typeName: name,
            id: fluid.allocateGuid()
        } : null;
    };
    
    /** A combined "component and grade name" which allows type tags to be declaratively constructed
     * from options material */
    
    fluid.typeFount = function (options) {
        var that = fluid.initLittleComponent("fluid.typeFount", options);
        return fluid.typeTag(that.options.targetTypeName);
    };
    
    /**
     * Creates a new "little component": a that-ist object with options merged into it by the framework.
     * This method is a convenience for creating small objects that have options but don't require full
     * View-like features such as the DOM Binder or events
     * 
     * @param {Object} name the name of the little component to create
     * @param {Object} options user-supplied options to merge with the defaults
     */
    // NOTE: the 3rd argument localOptions is NOT to be advertised as part of the stable API, it is present
    // just to allow backward compatibility whilst grade specifications are not mandatory
    fluid.initLittleComponent = function (name, options, localOptions) {
        var that = fluid.typeTag(name);
        // TODO: nickName must be available earlier than other merged options so that component may resolve to itself
        that.nickName = options && options.nickName ? options.nickName : fluid.computeNickName(that.typeName);
        localOptions = localOptions || {gradeNames: "fluid.littleComponent"};
        
        fluid.mergeComponentOptions(that, name, options, localOptions);
        fluid.initLifecycleFunctions(that);
        fluid.fireEvent(that.options.preInitFunction, that);

        if (fluid.hasGrade(that.options, "fluid.eventedComponent")) {
            fluid.instantiateFirers(that, that.options);
        }
        if (!fluid.hasGrade(that.options, "autoInit")) {
            fluid.clearLifecycleFunctions(that.options);
        }
        return that;
    };
    
    fluid.initLifecycleFunctions = function (that) {
        fluid.each(fluid.lifecycleFunctions, function (func, key) {
            var value = that.options[key];
            if (value) {
                that.options[key] = fluid.makeEventFirer(null, null, key);
                fluid.event.addListenerToFirer(that.options[key], value);
            }  
        }); 
    };
    
    fluid.clearLifecycleFunctions = function (options) {
        fluid.each(fluid.lifecycleFunctions, function (value, key) {
            delete options[key];
        });
        delete options.initFunction; 
    };

    fluid.diagnoseFailedView = fluid.identity;    
    
    fluid.initComponent = function (componentName, initArgs) {
        var options = fluid.defaults(componentName);
        if (!options.gradeNames) {
            fluid.fail("Cannot initialise component " + componentName + " which has no gradeName registered");
        }
        var args = [componentName].concat(fluid.makeArray(initArgs)); // TODO: support different initFunction variants
        var that = fluid.invokeGlobalFunction(options.initFunction, args);
        fluid.diagnoseFailedView(componentName, that, options, args);
        fluid.fireEvent(that.options.postInitFunction, that);
        if (fluid.initDependents) {
            fluid.initDependents(that);
        }
        fluid.fireEvent(that.options.finalInitFunction, that);
        fluid.clearLifecycleFunctions(that.options);
        return that.options.returnedPath ? fluid.get(that, that.options.returnedPath) : that;
    };

    // unsupported, NON-API function
    fluid.initSubcomponentImpl = function (that, entry, args) {
        var togo;
        if (typeof (entry) !== "function") {
            var entryType = typeof (entry) === "string" ? entry : entry.type;
            var globDef = fluid.defaults(true, entryType);
            fluid.merge("reverse", that.options, globDef);
            togo = entryType === "fluid.emptySubcomponent" ?
                fluid.emptySubcomponent(entry.options) : 
                fluid.invokeGlobalFunction(entryType, args);
        } else {
            togo = entry.apply(null, args);
        }

        var returnedOptions = togo ? togo.returnedOptions : null;
        if (returnedOptions) {
            fluid.merge(that.options.mergePolicy, that.options, returnedOptions);
            if (returnedOptions.listeners) {
                fluid.mergeListeners(that, that.events, returnedOptions.listeners);
            }
        }
        return togo;
    };
    
    /** Initialise all the "subcomponents" which are configured to be attached to 
     * the supplied top-level component, which share a particular "class name".
     * @param {Component} that The top-level component for which sub-components are
     * to be instantiated. It contains specifications for these subcomponents in its
     * <code>options</code> structure.
     * @param {String} className The "class name" or "category" for the subcomponents to
     * be instantiated. A class name specifies an overall "function" for a class of 
     * subcomponents and represents a category which accept the same signature of
     * instantiation arguments.
     * @param {Array of Object} args The instantiation arguments to be passed to each 
     * constructed subcomponent. These will typically be members derived from the
     * top-level <code>that</code> or perhaps globally discovered from elsewhere. One
     * of these arguments may be <code>fluid.COMPONENT_OPTIONS</code> in which case this
     * placeholder argument will be replaced by instance-specific options configured
     * into the member of the top-level <code>options</code> structure named for the
     * <code>className</code>
     * @return {Array of Object} The instantiated subcomponents, one for each member
     * of <code>that.options[className]</code>.
     */
    
    fluid.initSubcomponents = function (that, className, args) {
        var entry = that.options[className];
        if (!entry) {
            return;
        }
        var entries = $.makeArray(entry);
        var optindex = -1;
        var togo = [];
        args = $.makeArray(args);
        for (var i = 0; i < args.length; ++i) {
            if (args[i] === fluid.COMPONENT_OPTIONS) {
                optindex = i;
            }
        }
        for (i = 0; i < entries.length; ++i) {
            entry = entries[i];
            if (optindex !== -1) {
                args[optindex] = entry.options;
            }
            togo[i] = fluid.initSubcomponentImpl(that, entry, args);
        }
        return togo;
    };
        
    fluid.initSubcomponent = function (that, className, args) {
        return fluid.initSubcomponents(that, className, args)[0];
    };


    // Message resolution and templating
   
   
   /**
    * Converts a string to a regexp with the specified flags given in parameters
    * @param {String} a string that has to be turned into a regular expression
    * @param {String} the flags to provide to the reg exp 
    */
    fluid.stringToRegExp = function (str, flags) {
        return new RegExp(str.replace(/[\-\[\]{}()*+?.,\\\^$|#\s]/g, "\\$&"), flags);
    };
    
    /**
     * Simple string template system. 
     * Takes a template string containing tokens in the form of "%value".
     * Returns a new string with the tokens replaced by the specified values.
     * Keys and values can be of any data type that can be coerced into a string. Arrays will work here as well.
     * 
     * @param {String}    template    a string (can be HTML) that contains tokens embedded into it
     * @param {object}    values      a collection of token keys and values
     */
    fluid.stringTemplate = function (template, values) {
        var keys = fluid.keys(values);
        keys = keys.sort(fluid.compareStringLength());
        for (var i = 0; i < keys.length; ++i) {
            var key = keys[i];
            var re = fluid.stringToRegExp("%" + key, "g");
            template = template.replace(re, values[key]);
        }
        return template;
    };
    

    fluid.messageResolver = function (options) {
        var that = fluid.initLittleComponent("fluid.messageResolver", options);
        that.messageBase = that.options.parseFunc(that.options.messageBase);
        
        that.lookup = function (messagecodes) {
            var resolved = fluid.messageResolver.resolveOne(that.messageBase, messagecodes);
            if (resolved === undefined) {
                return fluid.find(that.options.parents, function (parent) {
                    return parent.lookup(messagecodes);
                });
            } else {
                return {template: resolved, resolveFunc: that.options.resolveFunc};
            }
        };
        that.resolve = function (messagecodes, args) {
            if (!messagecodes) {
                return "[No messagecodes provided]";
            }
            messagecodes = fluid.makeArray(messagecodes);
            var looked = that.lookup(messagecodes);
            return looked ? looked.resolveFunc(looked.template, args) :
                "[Message string for key " + messagecodes[0] + " not found]";
        };
        
        return that;  
    };
    
    fluid.defaults("fluid.messageResolver", {
        mergePolicy: {
            messageBase: "preserve",
            parents: "nomerge"
        },
        resolveFunc: fluid.stringTemplate,
        parseFunc: fluid.identity,
        messageBase: {},
        parents: []
    });
    
    fluid.messageResolver.resolveOne = function (messageBase, messagecodes) {
        for (var i = 0; i < messagecodes.length; ++i) {
            var code = messagecodes[i];
            var message = messageBase[code];
            if (message !== undefined) {
                return message;
            }
        }
    };
          
    /** Converts a data structure consisting of a mapping of keys to message strings,
     * into a "messageLocator" function which maps an array of message codes, to be 
     * tried in sequence until a key is found, and an array of substitution arguments,
     * into a substituted message string.
     */
    fluid.messageLocator = function (messageBase, resolveFunc) {
        var resolver = fluid.messageResolver({messageBase: messageBase, resolveFunc: resolveFunc});
        return function (messagecodes, args) {
            return resolver.resolve(messagecodes, args);
        };
    };

})(jQuery, fluid_1_5);
/*
Copyright 2007-2010 University of Cambridge
Copyright 2007-2009 University of Toronto
Copyright 2010-2011 Lucendo Development Ltd.
Copyright 2010 OCAD University

Licensed under the Educational Community License (ECL), Version 2.0 or the New
BSD license. You may not use this file except in compliance with one these
Licenses.

You may obtain a copy of the ECL 2.0 License and BSD License at
https://github.com/fluid-project/infusion/raw/master/Infusion-LICENSE.txt
*/

/** This file contains functions which depend on the presence of a DOM document
 * but which do not depend on the contents of Fluid.js **/

// Declare dependencies
/*global fluid_1_5:true, jQuery*/

// JSLint options 
/*jslint white: true, funcinvoke: true, undef: true, newcap: true, nomen: true, regexp: true, bitwise: true, browser: true, forin: true, maxerr: 100, indent: 4 */

var fluid_1_5 = fluid_1_5 || {};

(function ($, fluid) {

    // Private constants.
    var NAMESPACE_KEY = "fluid-scoped-data";

    /**
     * Gets stored state from the jQuery instance's data map.
     * This function is unsupported: It is not really intended for use by implementors.
     */
    fluid.getScopedData = function(target, key) {
        var data = $(target).data(NAMESPACE_KEY);
        return data ? data[key] : undefined;
    };

    /**
     * Stores state in the jQuery instance's data map. Unlike jQuery's version,
     * accepts multiple-element jQueries.
     * This function is unsupported: It is not really intended for use by implementors.
     */
    fluid.setScopedData = function(target, key, value) {
        $(target).each(function() {
            var data = $.data(this, NAMESPACE_KEY) || {};
            data[key] = value;

            $.data(this, NAMESPACE_KEY, data);
        });
    };

    /** Global focus manager - makes use of "focusin" event supported in jquery 1.4.2 or later.
     */

    var lastFocusedElement = null;
    
    $(document).bind("focusin", function(event){
        lastFocusedElement = event.target;
    });
    
    fluid.getLastFocusedElement = function() {
        return lastFocusedElement;
    }


    var ENABLEMENT_KEY = "enablement";

    /** Queries or sets the enabled status of a control. An activatable node
     * may be "disabled" in which case its keyboard bindings will be inoperable
     * (but still stored) until it is reenabled again.
     * This function is unsupported: It is not really intended for use by implementors.
     */
     
    fluid.enabled = function(target, state) {
        target = $(target);
        if (state === undefined) {
            return fluid.getScopedData(target, ENABLEMENT_KEY) !== false;
        }
        else {
            $("*", target).add(target).each(function() {
                if (fluid.getScopedData(this, ENABLEMENT_KEY) !== undefined) {
                    fluid.setScopedData(this, ENABLEMENT_KEY, state);
                }
                else if (/select|textarea|input/i.test(this.nodeName)) {
                    $(this).prop("disabled", !state);
                }
            });
            fluid.setScopedData(target, ENABLEMENT_KEY, state);
        }
    };
    
    fluid.initEnablement = function(target) {
        fluid.setScopedData(target, ENABLEMENT_KEY, true);
    };
    
    // This function is necessary since simulation of focus events by jQuery under IE
    // is not sufficiently good to intercept the "focusin" binding. Any code which triggers
    // focus or blur synthetically throughout the framework and client code must use this function,
    // especially if correct cross-platform interaction is required with the "deadMansBlur" function.
    
    function applyOp(node, func) {
        node = $(node);
        node.trigger("fluid-"+func);
        node[func]();
    }
    
    $.each(["focus", "blur"], function(i, name) {
        fluid[name] = function(elem) {
            applyOp(elem, name);
        }
    });
    
})(jQuery, fluid_1_5);
/*
Copyright 2008-2010 University of Cambridge
Copyright 2008-2009 University of Toronto

Licensed under the Educational Community License (ECL), Version 2.0 or the New
BSD license. You may not use this file except in compliance with one these
Licenses.

You may obtain a copy of the ECL 2.0 License and BSD License at
https://github.com/fluid-project/infusion/raw/master/Infusion-LICENSE.txt
*/

// Declare dependencies
/*global fluid_1_5:true, jQuery */

// JSLint options 
/*jslint white: true, funcinvoke: true, undef: true, newcap: true, nomen: true, regexp: true, bitwise: true, browser: true, forin: true, maxerr: 100, indent: 4 */

var fluid_1_5 = fluid_1_5 || {};

(function ($, fluid) {
    
    fluid.dom = fluid.dom || {};
    
    // Node walker function for iterateDom.
    var getNextNode = function (iterator) {
        if (iterator.node.firstChild) {
            iterator.node = iterator.node.firstChild;
            iterator.depth += 1;
            return iterator;
        }
        while (iterator.node) {
            if (iterator.node.nextSibling) {
                iterator.node = iterator.node.nextSibling;
                return iterator;
            }
            iterator.node = iterator.node.parentNode;
            iterator.depth -= 1;
        }
        return iterator;
    };
    
    /**
     * Walks the DOM, applying the specified acceptor function to each element.
     * There is a special case for the acceptor, allowing for quick deletion of elements and their children.
     * Return "delete" from your acceptor function if you want to delete the element in question.
     * Return "stop" to terminate iteration. 
     
     * Implementation note - this utility exists mainly for performance reasons. It was last tested
     * carefully some time ago (around jQuery 1.2) but at that time was around 3-4x faster at raw DOM
     * filtration tasks than the jQuery equivalents, which was an important source of performance loss in the
     * Reorderer component. General clients of the framework should use this method with caution if at all, and
     * the performance issues should be reassessed when we have time. 
     * 
     * @param {Element} node the node to start walking from
     * @param {Function} acceptor the function to invoke with each DOM element
     * @param {Boolean} allnodes Use <code>true</code> to call acceptor on all nodes, 
     * rather than just element nodes (type 1)
     */
    fluid.dom.iterateDom = function (node, acceptor, allNodes) {
        var currentNode = {node: node, depth: 0};
        var prevNode = node;
        var condition;
        while (currentNode.node !== null && currentNode.depth >= 0 && currentNode.depth < fluid.dom.iterateDom.DOM_BAIL_DEPTH) {
            condition = null;
            if (currentNode.node.nodeType === 1 || allNodes) {
                condition = acceptor(currentNode.node, currentNode.depth);
            }
            if (condition) {
                if (condition === "delete") {
                    currentNode.node.parentNode.removeChild(currentNode.node);
                    currentNode.node = prevNode;
                }
                else if (condition === "stop") {
                    return currentNode.node;
                }
            }
            prevNode = currentNode.node;
            currentNode = getNextNode(currentNode);
        }
    };
    
    // Work around IE circular DOM issue. This is the default max DOM depth on IE.
    // http://msdn2.microsoft.com/en-us/library/ms761392(VS.85).aspx
    fluid.dom.iterateDom.DOM_BAIL_DEPTH = 256;
    
    /**
     * Checks if the specified container is actually the parent of containee.
     * 
     * @param {Element} container the potential parent
     * @param {Element} containee the child in question
     */
    fluid.dom.isContainer = function (container, containee) {
        for (; containee; containee = containee.parentNode) {
            if (container === containee) {
                return true;
            }
        }
        return false;
    };
       
    /** Return the element text from the supplied DOM node as a single String.
     * Implementation note - this is a special-purpose utility used in the framework in just one
     * position in the Reorderer. It only performs a "shallow" traversal of the text and was intended
     * as a quick and dirty means of extracting element labels where the user had not explicitly provided one.
     * It should not be used by general users of the framework and its presence here needs to be 
     * reassessed.
     */
    fluid.dom.getElementText = function (element) {
        var nodes = element.childNodes;
        var text = "";
        for (var i = 0; i < nodes.length; ++i) {
            var child = nodes[i];
            if (child.nodeType === 3) {
                text = text + child.nodeValue;
            }
        }
        return text; 
    };
    
})(jQuery, fluid_1_5);
/*
Copyright 2008-2010 University of Cambridge
Copyright 2008-2009 University of Toronto
Copyright 2010 Lucendo Development Ltd.

Licensed under the Educational Community License (ECL), Version 2.0 or the New
BSD license. You may not use this file except in compliance with one these
Licenses.

You may obtain a copy of the ECL 2.0 License and BSD License at
https://github.com/fluid-project/infusion/raw/master/Infusion-LICENSE.txt
*/

// Declare dependencies
/*global fluid_1_5:true, jQuery*/

// JSLint options 
/*jslint white: true, funcinvoke: true, undef: true, newcap: true, nomen: true, regexp: true, bitwise: true, browser: true, forin: true, maxerr: 100, indent: 4 */

fluid_1_5 = fluid_1_5 || {};

(function ($, fluid) {
      
  var unUnicode = /(\\u[\dabcdef]{4}|\\x[\dabcdef]{2})/g;
  
  fluid.unescapeProperties = function (string) {
    string = string.replace(unUnicode, function(match) {
      var code = match.substring(2);
      var parsed = parseInt(code, 16);
      return String.fromCharCode(parsed);
      }
    );
    var pos = 0;
    while (true) {
        var backpos = string.indexOf("\\", pos);
        if (backpos === -1) {
            break;
        }
        if (backpos === string.length - 1) {
          return [string.substring(0, string.length - 1), true];
        }
        var replace = string.charAt(backpos + 1);
        if (replace === "n") replace = "\n";
        if (replace === "r") replace = "\r";
        if (replace === "t") replace = "\t";
        string = string.substring(0, backpos) + replace + string.substring(backpos + 2);
        pos = backpos + 1;
    }
    return [string, false];
  };
  
  var breakPos = /[^\\][\s:=]/;
  
  fluid.parseJavaProperties = function(text) {
    // File format described at http://java.sun.com/javase/6/docs/api/java/util/Properties.html#load(java.io.Reader)
    var togo = {};
    text = text.replace(/\r\n/g, "\n");
    text = text.replace(/\r/g, "\n");
    lines = text.split("\n");
    var contin, key, valueComp, valueRaw, valueEsc;
    for (var i = 0; i < lines.length; ++ i) {
      var line = $.trim(lines[i]);
      if (!line || line.charAt(0) === "#" || line.charAt(0) === '!') {
          continue;
      }
      if (!contin) {
        valueComp = "";
        var breakpos = line.search(breakPos);
        if (breakpos === -1) {
          key = line;
          valueRaw = "";
          }
        else {
          key = $.trim(line.substring(0, breakpos + 1)); // +1 since first char is escape exclusion
          valueRaw = $.trim(line.substring(breakpos + 2));
          if (valueRaw.charAt(0) === ":" || valueRaw.charAt(0) === "=") {
            valueRaw = $.trim(valueRaw.substring(1));
          }
        }
      
        key = fluid.unescapeProperties(key)[0];
        valueEsc = fluid.unescapeProperties(valueRaw);
      }
      else {
        valueEsc = fluid.unescapeProperties(line);
      }

      contin = valueEsc[1];
      if (!valueEsc[1]) { // this line was not a continuation line - store the value
        togo[key] = valueComp + valueEsc[0];
      }
      else {
        valueComp += valueEsc[0];
      }
    }
    return togo;
  };
      
    /** 
     * Expand a message string with respect to a set of arguments, following a basic
     * subset of the Java MessageFormat rules. 
     * http://java.sun.com/j2se/1.4.2/docs/api/java/text/MessageFormat.html
     * 
     * The message string is expected to contain replacement specifications such
     * as {0}, {1}, {2}, etc.
     * @param messageString {String} The message key to be expanded
     * @param args {String/Array of String} An array of arguments to be substituted into the message.
     * @return The expanded message string. 
     */
    fluid.formatMessage = function (messageString, args) {
        if (!args) {
            return messageString;
        } 
        if (typeof(args) === "string") {
            args = [args];
        }
        for (var i = 0; i < args.length; ++ i) {
            messageString = messageString.replace("{" + i + "}", args[i]);
        }
        return messageString;
    };
      
})(jQuery, fluid_1_5);
/*
Copyright 2007-2010 University of Cambridge
Copyright 2007-2009 University of Toronto
Copyright 2007-2009 University of California, Berkeley
Copyright 2010 OCAD University
Copyright 2010-2011 Lucendo Development Ltd.

Licensed under the Educational Community License (ECL), Version 2.0 or the New
BSD license. You may not use this file except in compliance with one these
Licenses.

You may obtain a copy of the ECL 2.0 License and BSD License at
https://github.com/fluid-project/infusion/raw/master/Infusion-LICENSE.txt
*/

// Declare dependencies
/*global fluid:true, fluid_1_5:true, jQuery*/

// JSLint options 
/*jslint white: true, funcinvoke: true, undef: true, newcap: true, nomen: true, regexp: true, bitwise: true, browser: true, forin: true, maxerr: 100, indent: 4 */

var fluid_1_5 = fluid_1_5 || {};
var fluid = fluid || fluid_1_5;

(function ($, fluid) {
       
    fluid.renderTimestamp = function (date) {
        var zeropad = function (num, width) {
             if (!width) width = 2;
             var numstr = (num == undefined? "" : num.toString());
             return "00000".substring(5 - width + numstr.length) + numstr;
             }
        return zeropad(date.getHours()) + ":" + zeropad(date.getMinutes()) + ":" + zeropad(date.getSeconds()) + "." + zeropad(date.getMilliseconds(), 3);
    };

    fluid.isTracing = true;

    fluid.registerNamespace("fluid.tracing");

    fluid.tracing.pathCount = [];
    
    fluid.tracing.summarisePathCount = function (pathCount) {
        pathCount = pathCount || fluid.tracing.pathCount;
        var togo = {};
        for (var i = 0; i < pathCount.length; ++ i) {
            var path = pathCount[i];
            if (!togo[path]) {
                togo[path] = 1;
            }
            else {
                ++togo[path];
            }
        }
        var toReallyGo = [];
        fluid.each(togo, function(el, path) {
            toReallyGo.push({path: path, count: el});
        });
        toReallyGo.sort(function(a, b) {return b.count - a.count});
        return toReallyGo;
    };
    
    fluid.tracing.condensePathCount = function (prefixes, pathCount) {
        prefixes = fluid.makeArray(prefixes);
        var prefixCount = {};
        fluid.each(prefixes, function(prefix) {
            prefixCount[prefix] = 0;
        });
        var togo = [];
        fluid.each(pathCount, function(el) {
            var path = el.path;
            if (!fluid.find(prefixes, function(prefix) {
                if (path.indexOf(prefix) === 0) {
                    prefixCount[prefix] += el.count;
                    return true;
                }
            })) {
            togo.push(el);
            }
        });
        fluid.each(prefixCount, function(count, path) {
            togo.unshift({path: path, count: count});
        });
        return togo;
    };

    // Exception stripping code taken from https://github.com/emwendelin/javascript-stacktrace/blob/master/stacktrace.js
    // BSD licence, see header
    
    fluid.detectStackStyle = function (e) {
        var style = "other";
        var stackStyle = {
            offset: 0  
        };
        if (e["arguments"]) {
            style = "chrome";
        } else if (typeof window !== "undefined" && window.opera && e.stacktrace) {
            style = "opera10";
        } else if (e.stack) {
            style = "firefox";
            // Detect FireFox 4-style stacks which are 1 level less deep
            stackStyle.offset = e.stack.indexOf("Trace exception") === -1? 1 : 0;
        } else if (typeof window !== 'undefined' && window.opera && !('stacktrace' in e)) { //Opera 9-
            style = "opera";
        }
        stackStyle.style = style;
        return stackStyle;
    };
    
    fluid.obtainException = function() {
        try {
            throw new Error("Trace exception");
        }
        catch (e) {
            return e;
        }
    };
    
    var stackStyle = fluid.detectStackStyle(fluid.obtainException());

    fluid.registerNamespace("fluid.exceptionDecoders");
    
    fluid.decodeStack = function() {
        if (stackStyle.style !== "firefox") {
            return null;
        }
        var e = fluid.obtainException();
        return fluid.exceptionDecoders[stackStyle.style](e);
    };

    fluid.exceptionDecoders.firefox = function(e) {
        var lines = e.stack.replace(/(?:\n@:0)?\s+$/m, '').replace(/^\(/gm, '{anonymous}(').split('\n');
        return fluid.transform(lines, function(line) {
            var atind = line.indexOf("@");
            return atind === -1? [line] : [line.substring(atind + 1), line.substring(0, atind)];  
        });
    };
    
    fluid.getCallerInfo = function(atDepth) {
        atDepth = (atDepth || 3) - stackStyle.offset;
        var stack = fluid.decodeStack();
        return stack? stack[atDepth][0] : null;
    };
    
    function generate(c, count) {
        var togo = "";
        for (var i = 0; i < count; ++ i) {
            togo += c;
        }
        return togo;
    }
    
    function printImpl(obj, small, options) {
        var big = small + options.indentChars;
        if (obj === null) {
            return "null";
        }
        else if (fluid.isPrimitive(obj)) {
            return JSON.stringify(obj);
        }
        else {
            var j = [];
            if (fluid.isArrayable(obj)) {
                if (obj.length === 0) {
                    return "[]";
                }
                for (var i = 0; i < obj.length; ++ i) {
                    j[i] = printImpl(obj[i], big, options);
                }
                return "[\n" + big + j.join(",\n" + big) + "\n" + small + "]";
                }
            else {
                var i = 0;
                fluid.each(obj, function(value, key) {
                    j[i++] = JSON.stringify(key) + ": " + printImpl(value, big, options);
                });
                return "{\n" + big + j.join(",\n" + big) + "\n" + small + "}"; 
            }
        }
    }
    
    fluid.prettyPrintJSON = function(obj, options) {
        options = $.extend({indent: 4}, options);
        options.indentChars = generate(" ", options.indent);
        return printImpl(obj, "", options);
    }
        
    /** 
     * Dumps a DOM element into a readily recognisable form for debugging - produces a
     * "semi-selector" summarising its tag name, class and id, whichever are set.
     * 
     * @param {jQueryable} element The element to be dumped
     * @return A string representing the element.
     */
    fluid.dumpEl = function (element) {
        var togo;
        
        if (!element) {
            return "null";
        }
        if (element.nodeType === 3 || element.nodeType === 8) {
            return "[data: " + element.data + "]";
        } 
        if (element.nodeType === 9) {
            return "[document: location " + element.location + "]";
        }
        if (!element.nodeType && fluid.isArrayable(element)) {
            togo = "[";
            for (var i = 0; i < element.length; ++ i) {
                togo += fluid.dumpEl(element[i]);
                if (i < element.length - 1) {
                    togo += ", ";
                }
            }
            return togo + "]";
        }
        element = $(element);
        togo = element.get(0).tagName;
        if (element.id) {
            togo += "#" + element.id;
        }
        if (element.attr("class")) {
            togo += "." + element.attr("class");
        }
        return togo;
    };
        
})(jQuery, fluid_1_5);
    /*
Copyright 2008-2010 University of Cambridge
Copyright 2008-2009 University of Toronto
Copyright 2010-2011 Lucendo Development Ltd.
Copyright 2010 OCAD University

Licensed under the Educational Community License (ECL), Version 2.0 or the New
BSD license. You may not use this file except in compliance with one these
Licenses.

You may obtain a copy of the ECL 2.0 License and BSD License at
https://github.com/fluid-project/infusion/raw/master/Infusion-LICENSE.txt
*/

// Declare dependencies
/*global fluid_1_5:true, jQuery*/

// JSLint options 
/*jslint white: true, funcinvoke: true, continue: true, elsecatch: true, operator: true, jslintok:true, undef: true, newcap: true, regexp: true, bitwise: true, browser: true, forin: true, maxerr: 100, indent: 4 */

var fluid_1_5 = fluid_1_5 || {};

(function ($, fluid) {
    
    fluid.BINDING_ROOT_KEY = "fluid-binding-root";
    
    /** Recursively find any data stored under a given name from a node upwards
     * in its DOM hierarchy **/
     
    fluid.findData = function (elem, name) {
        while (elem) {
            var data = $.data(elem, name);
            if (data) {
                return data;
            }
            elem = elem.parentNode;
        }
    };
  
    fluid.bindFossils = function (node, data, fossils) {
        $.data(node, fluid.BINDING_ROOT_KEY, {data: data, fossils: fossils});
    };
        
    fluid.boundPathForNode = function (node, fossils) {
        node = fluid.unwrap(node);
        var key = node.name || node.id;
        var record = fossils[key];
        return record ? record.EL : null;
    };
  
    fluid.findForm = function (node) {
        return fluid.findAncestor(node, function (element) {
            return element.nodeName.toLowerCase() === "form";
        });
    };
    
    /** A generalisation of jQuery.val to correctly handle the case of acquiring and
     * setting the value of clustered radio button/checkbox sets, potentially, given
     * a node corresponding to just one element.
     */
    fluid.value = function (nodeIn, newValue) {
        var node = fluid.unwrap(nodeIn);
        var multiple = false;
        if (node.nodeType === undefined && node.length > 1) {
            node = node[0];
            multiple = true;
        }
        if ("input" !== node.nodeName.toLowerCase() || !/radio|checkbox/.test(node.type)) {
            // resist changes to contract of jQuery.val() in jQuery 1.5.1 (see FLUID-4113)
            return newValue === undefined ? $(node).val() : $(node).val(newValue);
        }
        var name = node.name;
        if (name === undefined) {
            fluid.fail("Cannot acquire value from node " + fluid.dumpEl(node) + " which does not have name attribute set");
        }
        var elements;
        if (multiple) {
            elements = nodeIn;
        } else {
            elements = node.ownerDocument.getElementsByName(name);
            var scope = fluid.findForm(node);
            elements = $.grep(elements, function (element) {
                if (element.name !== name) {
                    return false;
                }
                return !scope || fluid.dom.isContainer(scope, element);
            });
        }
        if (newValue !== undefined) {
            if (typeof(newValue) === "boolean") {
                newValue = (newValue ? "true" : "false");
            }
          // jQuery gets this partially right, but when dealing with radio button array will
          // set all of their values to "newValue" rather than setting the checked property
          // of the corresponding control. 
            $.each(elements, function () {
                this.checked = (newValue instanceof Array ? 
                    $.inArray(this.value, newValue) !== -1 : newValue === this.value);
            });
        } else { // this part jQuery will not do - extracting value from <input> array
            var checked = $.map(elements, function (element) {
                return element.checked ? element.value : null;
            });
            return node.type === "radio" ? checked[0] : checked;
        }
    };
    
   /** "Automatically" apply to whatever part of the data model is
     * relevant, the changed value received at the given DOM node*/
    fluid.applyBoundChange = function (node, newValue, applier) {
        node = fluid.unwrap(node);
        if (newValue === undefined) {
            newValue = fluid.value(node);
        }
        if (node.nodeType === undefined && node.length > 0) {
            node = node[0];
        } // assume here that they share name and parent
        var root = fluid.findData(node, fluid.BINDING_ROOT_KEY);
        if (!root) {
            fluid.fail("Bound data could not be discovered in any node above " + fluid.dumpEl(node));
        }
        var name = node.name;
        var fossil = root.fossils[name];
        if (!fossil) {
            fluid.fail("No fossil discovered for name " + name + " in fossil record above " + fluid.dumpEl(node));
        }
        if (typeof(fossil.oldvalue) === "boolean") { // deal with the case of an "isolated checkbox"
            newValue = newValue[0] ? true : false;
        }
        var EL = root.fossils[name].EL;
        if (applier) {
            applier.fireChangeRequest({path: EL, value: newValue, source: node.id});
        } else {
            fluid.set(root.data, EL, newValue);
        }    
    };
    
    /** MODEL ACCESSOR ENGINE (trundler) **/
    
    /** Standard strategies for resolving path segments **/
    fluid.model.environmentStrategy = function (initEnvironment) {
        return {
            init: function () {
                var environment = initEnvironment;
                return function (root, segment, index) {
                    var togo;
                    if (environment && environment[segment]) {
                        togo = environment[segment];
                    }
                    environment = null;
                    return togo; 
                };
            }
        };
    };

    fluid.model.defaultCreatorStrategy = function (root, segment) {
        if (root[segment] === undefined) {
            root[segment] = {};
            return root[segment];
        }
    };
    
    fluid.model.defaultFetchStrategy = function (root, segment) {
        return segment === "" ? root : root[segment];
    };
        
    fluid.model.funcResolverStrategy = function (root, segment) {
        if (root.resolvePathSegment) {
            return root.resolvePathSegment(segment);
        }
    };
    
        
    fluid.model.defaultGetConfig = {
        strategies: [fluid.model.funcResolverStrategy, fluid.model.defaultFetchStrategy]
    };

    fluid.model.defaultSetConfig = {
        strategies: [fluid.model.funcResolverStrategy, fluid.model.defaultFetchStrategy, fluid.model.defaultCreatorStrategy]
    };
    
    
    // unsupported, NON-API function
    fluid.model.applyStrategy = function (strategy, root, segment, index) {
        if (typeof (strategy) === "function") { 
            return strategy(root, segment, index);
        } else if (strategy && strategy.next) {
            return strategy.next(root, segment, index);
        }
    };
    
    // unsupported, NON-API function
    fluid.model.initStrategy = function (baseStrategy, index, oldStrategies) {
        return baseStrategy.init ? baseStrategy.init(oldStrategies ? oldStrategies[index] : undefined) : baseStrategy;
    };
    
    // unsupported, NON-API function
    fluid.model.makeTrundler = function (root, config, oldStrategies) {
        var that = {
            root: root,
            strategies: fluid.isArrayable(config) ? config : 
                fluid.transform(config.strategies, function (strategy, index) {
                    return fluid.model.initStrategy(strategy, index, oldStrategies); 
                })
        };
        that.trundle = function (EL, uncess) {
            uncess = uncess || 0;
            var newThat = fluid.model.makeTrundler(that.root, config, that.strategies);
            newThat.segs = fluid.model.parseEL(EL);
            newThat.index = 0;
            newThat.step(newThat.segs.length - uncess);
            return newThat;
        };
        that.next = function () {
            if (!that.root) {
                return;
            }
            var accepted;
            for (var i = 0; i < that.strategies.length; ++i) {
                var value = fluid.model.applyStrategy(that.strategies[i], that.root, that.segs[that.index], that.index);
                if (accepted === undefined) {
                    accepted = value;
                }
            }
            if (accepted === fluid.NO_VALUE) {
                accepted = undefined;
            }
            that.root = accepted;
            ++that.index;
        };
        that.step = function (limit) {
            for (var i = 0; i < limit; ++i) {
                that.next();
            }
            that.last = that.segs[that.index];
        };
        return that;
    };
    
    // unsupported, NON-API function
    // core trundling recursion point
    fluid.model.trundleImpl = function (trundler, EL, config, uncess) {
        if (typeof (EL) === "string") {
            trundler = trundler.trundle(EL, uncess);
        } else {
            var key = EL.type || "default";
            var resolver = config.resolvers[key];
            if (!resolver) {
                fluid.fail("Unable to find resolver of type " + key);
            }
            trundler = resolver(EL, trundler) || {};
            if (EL.path && trundler.trundle && trundler.root !== undefined) {
                trundler = fluid.model.trundleImpl(trundler, EL.path, config, uncess);
            }
        }
        return trundler;  
    };
        
    // unsupported, NON-API function
    // entry point for initially unbased trundling
    fluid.model.trundle = function (root, EL, config, uncess) {
        EL = EL || "";
        config = config || fluid.model.defaultGetConfig;
        var trundler = fluid.model.makeTrundler(root, config);
        return fluid.model.trundleImpl(trundler, EL, config, uncess);
    };
    
    fluid.model.getPenultimate = function (root, EL, config) {
        return fluid.model.trundle(root, EL, config, 1);
    };  
   
    // Implementation notes: The EL path manipulation utilities here are somewhat more thorough
    // and expensive versions of those provided in Fluid.js - there is some duplication of 
    // functionality. This is a tradeoff between stability and performance - the versions in
    // Fluid.js are the most frequently used and do not implement escaping of characters .
    // as \. and \ as \\ as the versions here. The implementations here are not quite complete
    // or very performant and are left here partially as an implementation note. Problems will
    // arise if clients manipulate JSON structures containing "." characters in keys as if they
    // are models, treating these is best left until the cases where they occur. The now standard
    // utilities fluid.path(), fluid.parseEL and fluid.composePath are the ones recommended for
    // general users and their implementation can be upgraded if required.
   
    fluid.pathUtil = {};
   
    var getPathSegmentImpl = function (accept, path, i) {
        var segment = null; // TODO: rewrite this with regexes and replaces
        if (accept) {
            segment = "";
        }
        var escaped = false;
        var limit = path.length;
        for (; i < limit; ++i) {
            var c = path.charAt(i);
            if (!escaped) {
                if (c === '.') {
                    break;
                }
                else if (c === '\\') {
                    escaped = true;
                }
                else if (segment !== null) {
                    segment += c;
                }
            }
            else {
                escaped = false;
                if (segment !== null) {
                    accept += c;
                }
            }
        }
        if (segment !== null) {
            accept[0] = segment;
        }
        return i;
    };
    
    var globalAccept = []; // TODO: serious reentrancy risk here, why is this impl like this?
    
    fluid.pathUtil.getPathSegment = function (path, i) {
        getPathSegmentImpl(globalAccept, path, i);
        return globalAccept[0];
    }; 
  
    fluid.pathUtil.getHeadPath = function (path) {
        return fluid.pathUtil.getPathSegment(path, 0);
    };
  
    fluid.pathUtil.getFromHeadPath = function (path) {
        var firstdot = getPathSegmentImpl(null, path, 0);
        return firstdot === path.length ? null
            : path.substring(firstdot + 1);
    };
    
    function lastDotIndex(path) {
        // TODO: proper escaping rules
        return path.lastIndexOf(".");
    }
    
    fluid.pathUtil.getToTailPath = function (path) {
        var lastdot = lastDotIndex(path);
        return lastdot === -1 ? null : path.substring(0, lastdot);
    };

  /** Returns the very last path component of a bean path */
    fluid.pathUtil.getTailPath = function (path) {
        var lastdot = lastDotIndex(path);
        return fluid.pathUtil.getPathSegment(path, lastdot + 1);
    };
    
    var composeSegment = function (prefix, toappend) {
        for (var i = 0; i < toappend.length; ++i) {
            var c = toappend.charAt(i);
            if (c === '.' || c === '\\' || c === '}') {
                prefix += '\\';
            }
            prefix += c;
        }
        return prefix;
    };
    
    /**
     * Compose a prefix and suffix EL path, where the prefix is already escaped.
     * Prefix may be empty, but not null. The suffix will become escaped.
     */
    fluid.pathUtil.composePath = function (prefix, suffix) {
        if (prefix.length !== 0) {
            prefix += '.';
        }
        return composeSegment(prefix, suffix);
    };    
   
    fluid.pathUtil.matchPath = function (spec, path) {
        var togo = "";
        while (true) {
            // FLUID-4625 - symmetry on spec and path is actually undesirable, but this
            // quickly avoids at least missed notifications - improved (but slower) 
            // implementation should explode composite changes
            if (!spec || !path) {
                break;
            }
            var spechead = fluid.pathUtil.getHeadPath(spec);
            var pathhead = fluid.pathUtil.getHeadPath(path);
            // if we fail to match on a specific component, fail.
            if (spechead !== "*" && spechead !== pathhead) {
                return null;
            }
            togo = fluid.pathUtil.composePath(togo, pathhead);
            spec = fluid.pathUtil.getFromHeadPath(spec);
            path = fluid.pathUtil.getFromHeadPath(path);
        }
        return togo;
    };
        
    /** CHANGE APPLIER **/    
      
    fluid.model.isNullChange = function (model, request, resolverGetConfig) {
        if (request.type === "ADD") {
            var existing = fluid.get(model, request.path, resolverGetConfig);
            if (existing === request.value) {
                return true;
            }
        }
    };
    /** Applies the supplied ChangeRequest object directly to the supplied model.
     */
    fluid.model.applyChangeRequest = function (model, request, resolverSetConfig) {
        var pen = fluid.model.getPenultimate(model, request.path, resolverSetConfig || fluid.model.defaultSetConfig);
        
        if (request.type === "ADD" || request.type === "MERGE") {
            if (request.path === "" || request.type === "MERGE") {
                if (request.type === "ADD") {
                    fluid.clear(pen.root);
                }
                $.extend(true, request.path === "" ? pen.root : pen.root[pen.last], request.value);
            }
            else {
                pen.root[pen.last] = request.value;
            }
        }
        else if (request.type === "DELETE") {
            if (request.path === "") {
                fluid.clear(pen.root);
            }
            else {
                delete pen.root[pen.last];
            }
        }
    };
          
    /** Add a listener to a ChangeApplier event that only acts in the case the event
     * has not come from the specified source (typically ourself)
     * @param modelEvent An model event held by a changeApplier (typically applier.modelChanged)
     * @param path The path specification to listen to
     * @param source The source value to exclude (direct equality used)
     * @param func The listener to be notified of a change
     * @param [eventName] - optional - the event name to be listened to - defaults to "modelChanged" 
     */
    fluid.addSourceGuardedListener = function(applier, path, source, func, eventName) {
        eventName = eventName || "modelChanged";
        applier[eventName].addListener(path, 
            function() {
                if (!applier.hasChangeSource(source)) {
                    func.apply(null, arguments);
                }
            });
    };

    /** Convenience method to fire a change event to a specified applier, including
     * a supplied "source" identified (perhaps for use with addSourceGuardedListener)
     */ 
    fluid.fireSourcedChange = function (applier, path, value, source) {
        applier.fireChangeRequest({
            path: path,
            value: value,
            source: source
        });         
    };
    
    /** Dispatches a list of changes to the supplied applier */
    fluid.requestChanges = function (applier, changes) {
        for (var i = 0; i < changes.length; ++i) {
            applier.fireChangeRequest(changes[i]);
        }  
    };
    
  
    // Utility shared between changeApplier and superApplier
    
    function bindRequestChange(that) {
        that.requestChange = function (path, value, type) {
            var changeRequest = {
                path: path,
                value: value,
                type: type
            };
            that.fireChangeRequest(changeRequest);
        };
    }
    
    // Utility used for source tracking in changeApplier
    
    function sourceWrapModelChanged(modelChanged, threadLocal) {
        return function(changeRequest) {
            var sources = threadLocal().sources;
            var args = arguments;
            var source = changeRequest.source || "";
            fluid.tryCatch(function() {
                if (sources[source] === undefined) {
                    sources[source] = 0;
                }
                ++sources[source];
                modelChanged.apply(null, args);
            }, null, function() {
                --sources[source];
            });
        };
    }
  
    fluid.makeChangeApplier = function (model, options) {
        options = options || {};
        var baseEvents = {
            guards: fluid.event.getEventFirer(false, true, "guard event"),
            postGuards: fluid.event.getEventFirer(false, true, "postGuard event"),
            modelChanged: fluid.event.getEventFirer(false, false, "modelChanged event")
        };
        var threadLocal = fluid.threadLocal(function() { return {sources: {}};});
        var that = {
        // For now, we don't use "id" to avoid confusing component detection which uses
        // a simple algorithm looking for that field
            changeid: fluid.allocateGuid(),
            model: model
        };
        
        function makeGuardWrapper(cullUnchanged) {
            if (!cullUnchanged) {
                return null;
            }
            var togo = function (guard) {
                return function (model, changeRequest, internalApplier) {
                    var oldRet = guard(model, changeRequest, internalApplier);
                    if (oldRet === false) {
                        return false;
                    }
                    else {
                        if (fluid.model.isNullChange(model, changeRequest)) {
                            togo.culled = true;
                            return false;
                        }
                    }
                };
            };
            return togo;
        }

        function wrapListener(listener, spec) {
            var pathSpec = spec;
            var transactional = false;
            var priority = Number.MAX_VALUE;
            if (typeof (spec) !== "string") {
                pathSpec = spec.path;
                transactional = spec.transactional;
                if (spec.priority !== undefined) {
                    priority = spec.priority;
                }
            }
            else {
                if (pathSpec.charAt(0) === "!") {
                    transactional = true;
                    pathSpec = pathSpec.substring(1);
                }
            }
            return function (changePath, fireSpec, accum) {
                var guid = fluid.event.identifyListener(listener);
                var exist = fireSpec.guids[guid];
                if (!exist) {
                    var match = fluid.pathUtil.matchPath(pathSpec, changePath);
                    if (match !== null) {
                        var record = {
                            changePath: changePath,
                            pathSpec: pathSpec,
                            listener: listener,
                            priority: priority,
                            transactional: transactional
                        };
                        if (accum) {
                            record.accumulate = [accum];
                        }
                        fireSpec.guids[guid] = record;
                        var collection = transactional ? "transListeners" : "listeners";
                        fireSpec[collection].push(record);
                        fireSpec.all.push(record);
                    }
                }
                else if (accum) {
                    if (!exist.accumulate) {
                        exist.accumulate = [];
                    }
                    exist.accumulate.push(accum);
                }
            };
        }
        
        function fireFromSpec(name, fireSpec, args, category, wrapper) {
            return baseEvents[name].fireToListeners(fireSpec[category], args, wrapper);
        }
        
        function fireComparator(recA, recB) {
            return recA.priority - recB.priority;
        }

        function prepareFireEvent(name, changePath, fireSpec, accum) {
            baseEvents[name].fire(changePath, fireSpec, accum);
            fireSpec.all.sort(fireComparator);
            fireSpec.listeners.sort(fireComparator);
            fireSpec.transListeners.sort(fireComparator);
        }
        
        function makeFireSpec() {
            return {guids: {}, all: [], listeners: [], transListeners: []};
        }
        
        function getFireSpec(name, changePath) {
            var fireSpec = makeFireSpec();
            prepareFireEvent(name, changePath, fireSpec);
            return fireSpec;
        }
        
        function fireEvent(name, changePath, args, wrapper) {
            var fireSpec = getFireSpec(name, changePath);
            return fireFromSpec(name, fireSpec, args, "all", wrapper);
        }
        
        function adaptListener(that, name) {
            that[name] = {
                addListener: function (spec, listener, namespace) {
                    baseEvents[name].addListener(wrapListener(listener, spec), namespace);
                },
                removeListener: function (listener) {
                    baseEvents[name].removeListener(listener);
                }
            };
        }
        adaptListener(that, "guards");
        adaptListener(that, "postGuards");
        adaptListener(that, "modelChanged");
        
        function preFireChangeRequest(changeRequest) {
            if (!changeRequest.type) {
                changeRequest.type = "ADD";
            }
        }

        var bareApplier = {
            fireChangeRequest: function (changeRequest) {
                that.fireChangeRequest(changeRequest, true);
            }
        };
        bindRequestChange(bareApplier);

        that.fireChangeRequest = function (changeRequest, defeatGuards) {
            preFireChangeRequest(changeRequest);
            var guardFireSpec = defeatGuards ? null : getFireSpec("guards", changeRequest.path);
            if (guardFireSpec && guardFireSpec.transListeners.length > 0) {
                var ation = that.initiate();
                ation.fireChangeRequest(changeRequest, guardFireSpec);
                ation.commit();
            }
            else {
                if (!defeatGuards) {
                    // TODO: this use of "listeners" seems pointless since we have just verified that there are no transactional listeners
                    var prevent = fireFromSpec("guards", guardFireSpec, [model, changeRequest, bareApplier], "listeners");
                    if (prevent === false) {
                        return false;
                    }
                }
                var oldModel = model;
                if (!options.thin) {
                    oldModel = {};
                    fluid.model.copyModel(oldModel, model);                    
                }
                fluid.model.applyChangeRequest(model, changeRequest, options.resolverSetConfig);
                fireEvent("modelChanged", changeRequest.path, [model, oldModel, [changeRequest]]);
            }
        };
        
        that.fireChangeRequest = sourceWrapModelChanged(that.fireChangeRequest, threadLocal);
        bindRequestChange(that);

        function fireAgglomerated(eventName, formName, changes, args, accpos) {
            var fireSpec = makeFireSpec();
            for (var i = 0; i < changes.length; ++i) {
                prepareFireEvent(eventName, changes[i].path, fireSpec, changes[i]);
            }
            for (var j = 0; j < fireSpec[formName].length; ++j) {
                var spec = fireSpec[formName][j];
                if (accpos) {
                    args[accpos] = spec.accumulate;
                }
                var ret = spec.listener.apply(null, args);
                if (ret === false) {
                    return false;
                }
            }
        }

        that.initiate = function (newModel) {
            var cancelled = false;
            var changes = [];
            if (options.thin) {
                newModel = model;
            }
            else {
                newModel = newModel || {};
                fluid.model.copyModel(newModel, model);
            }
            // the guard in the inner world is given a private applier to "fast track"
            // and glob collateral changes it requires
            var internalApplier = {
                fireChangeRequest: function (changeRequest) {
                    preFireChangeRequest(changeRequest);
                    fluid.model.applyChangeRequest(newModel, changeRequest, options.resolverSetConfig);
                    changes.push(changeRequest);
                }
            };
            bindRequestChange(internalApplier);
            var ation = {
                commit: function () {
                    var oldModel;
                    if (cancelled) {
                        return false;
                    }
                    var ret = fireAgglomerated("postGuards", "transListeners", changes, [newModel, null, internalApplier], 1);
                    if (ret === false) {
                        return false;
                    }
                    if (options.thin) {
                        oldModel = model;
                    }
                    else {
                        oldModel = {};
                        fluid.model.copyModel(oldModel, model);
                        fluid.clear(model);
                        fluid.model.copyModel(model, newModel);
                    }
                    fireAgglomerated("modelChanged", "all", changes, [model, oldModel, null], 2);
                },
                fireChangeRequest: function (changeRequest) {
                    preFireChangeRequest(changeRequest);
                    if (options.cullUnchanged && fluid.model.isNullChange(model, changeRequest, options.resolverGetConfig)) {
                        return;
                    } 
                    var wrapper = makeGuardWrapper(options.cullUnchanged);
                    var prevent = fireEvent("guards", changeRequest.path, [newModel, changeRequest, internalApplier], wrapper);
                    if (prevent === false && !(wrapper && wrapper.culled)) {
                        cancelled = true;
                    }
                    if (!cancelled) {
                        if (!(wrapper && wrapper.culled)) {
                            fluid.model.applyChangeRequest(newModel, changeRequest, options.resolverSetConfig);
                            changes.push(changeRequest);
                        }
                    }
                }
            };
            
            ation.fireChangeRequest = sourceWrapModelChanged(ation.fireChangeRequest, threadLocal);
            bindRequestChange(ation);

            return ation;
        };
        
        that.hasChangeSource = function (source) {
            return threadLocal().sources[source] > 0;
        };
        
        return that;
    };
    
    fluid.makeSuperApplier = function () {
        var subAppliers = [];
        var that = {};
        that.addSubApplier = function (path, subApplier) {
            subAppliers.push({path: path, subApplier: subApplier});
        };
        that.fireChangeRequest = function (request) {
            for (var i = 0; i < subAppliers.length; ++i) {
                var path = subAppliers[i].path;
                if (request.path.indexOf(path) === 0) {
                    var subpath = request.path.substring(path.length + 1);
                    var subRequest = fluid.copy(request);
                    subRequest.path = subpath;
                    // TODO: Deal with the as yet unsupported case of an EL rvalue DAR
                    subAppliers[i].subApplier.fireChangeRequest(subRequest);
                }
            }
        };
        bindRequestChange(that);
        return that;
    };
    
    fluid.attachModel = function (baseModel, path, model) {
        var segs = fluid.model.parseEL(path);
        for (var i = 0; i < segs.length - 1; ++i) {
            var seg = segs[i];
            var subModel = baseModel[seg];
            if (!subModel) {
                baseModel[seg] = subModel = {};
            }
            baseModel = subModel;
        }
        baseModel[segs[segs.length - 1]] = model;
    };
    
    fluid.assembleModel = function (modelSpec) {
        var model = {};
        var superApplier = fluid.makeSuperApplier();
        var togo = {model: model, applier: superApplier};
        for (var path in modelSpec) {
            var rec = modelSpec[path];
            fluid.attachModel(model, path, rec.model);
            if (rec.applier) {
                superApplier.addSubApplier(path, rec.applier);
            }
        }
        return togo;
    };

})(jQuery, fluid_1_5);
/*
Copyright 2010 University of Toronto
Copyright 2010-2011 OCAD University

Licensed under the Educational Community License (ECL), Version 2.0 or the New
BSD license. You may not use this file except in compliance with one these
Licenses.

You may obtain a copy of the ECL 2.0 License and BSD License at
https://github.com/fluid-project/infusion/raw/master/Infusion-LICENSE.txt
*/

// Declare dependencies
/*global fluid:true, fluid_1_5:true, jQuery*/

// JSLint options 
/*jslint white: true, funcinvoke: true, undef: true, newcap: true, nomen: true, regexp: true, bitwise: true, browser: true, forin: true, maxerr: 100, indent: 4 */

var fluid_1_5 = fluid_1_5 || {};
var fluid = fluid || fluid_1_5;

(function ($) {

    fluid.model = fluid.model || {};
    fluid.model.transform = fluid.model.transform || {};
    
    
    /******************************
     * General Model Transformers *
     ******************************/
    
    fluid.model.transform.value = function (model, expandSpec, recurse) {
        var val;
        if (expandSpec.path) {
            val = fluid.get(model, expandSpec.path);
            
            if (typeof(val) !== "undefined") {
                return val;
            }
        }
        
        return typeof(expandSpec.value) === "object" ? recurse(model, expandSpec.value) : expandSpec.value;    
    };
    
    fluid.model.transform.arrayValue = function (model, expandSpec, recurse) {
        return fluid.makeArray(fluid.model.transform.value(model, expandSpec));
    };
     
    fluid.model.transform.count = function (model, expandSpec, recurse) {
        var value = fluid.get(model, expandSpec.path);
        return fluid.makeArray(value).length;
    };
     
    fluid.model.transform.firstValue = function (model, expandSpec, recurse) {
        var result;
        for (var i = 0; i < expandSpec.values.length; i++) {
            var value = expandSpec.values[i];
            if (typeof(value) === "string") {
                value = fixupExpandSpec(value);
            }
            result = fluid.model.transform.value(model, value.expander, recurse);
            if (typeof(result) !== "undefined") {
                break;
            }
        }
        return result;
    };
    
    var getOrRecurse = function (model, value, recurse) {
        return typeof(value) === "string" ? fluid.get(model, value) : recurse(model, value, recurse);
    };
    
    fluid.model.transform.merge = function (model, expandSpec, recurse) {
        var left = getOrRecurse(model, expandSpec.left, recurse);
        var right = getOrRecurse(model, expandSpec.right, recurse);
        
        if (typeof(left) !== "object" || typeof(right) !== "object") {
            return left;
        }
        
        return fluid.merge(expandSpec.policy ? expandSpec.policy : null, {}, left, right);
    };
     
    var fixupExpandSpec = function (expandSpec) {
        return {
            expander: {
                type: "fluid.model.transform.value",
                path: expandSpec
            }
        };
    };
    
    var expandRule = function (model, targetPath, rule) {
        var expanded = {};
        for (var key in rule) {
            var value = rule[key];
            if (key === "expander") {
                var expanderFn = fluid.getGlobalValue(value.type);
                if (expanderFn) {
                    expanded = expanderFn.call(null, model, value, fluid.model.transformWithRules);
                }
            } else {
                expanded[key] = fluid.model.transformWithRules(model, value);
            }
        }
        return expanded;
    };
    
    /**
     * Transforms a model based on a specified expansion rules objects.
     * Rules objects take the form of:
     *   {
     *       "target.path": "value.el.path" || {
     *          expander: {
     *              type: "expander.function.path",
     *               ...
     *           }
     *       }
     *   }
     *
     * @param {Object} model the model to transform
     * @param {Object} rules a rules object containing instructions on how to transform the model
     */
    fluid.model.transformWithRules = function (model, rules) {
        var transformed;
        rules = fluid.makeArray(rules);
        
        fluid.each(rules, function (rulesObj) {
            transformed = {};
            for (var targetPath in rulesObj) {
                var rule = rulesObj[targetPath];

                if (typeof(rule) === "string") {
                    rule = fixupExpandSpec(rule);
                }

                var expanded = expandRule(model, targetPath, rule);
                if (typeof(expanded) !== "undefined") {
                    fluid.set(transformed, targetPath, expanded);
                }
            };
            model = transformed;
        });
        return transformed;
    };
    
})(jQuery, fluid_1_5);
/*
Copyright 2008-2010 University of Cambridge
Copyright 2008-2010 University of Toronto
Copyright 2010-2011 Lucendo Development Ltd.
Copyright 2010-2011 OCAD University

Licensed under the Educational Community License (ECL), Version 2.0 or the New
BSD license. You may not use this file except in compliance with one these
Licenses.

You may obtain a copy of the ECL 2.0 License and BSD License at
https://github.com/fluid-project/infusion/raw/master/Infusion-LICENSE.txt
*/

// Declare dependencies
/*global fluid:true, fluid_1_5:true, jQuery*/

// JSLint options 
/*jslint white: true, funcinvoke: true, undef: true, newcap: true, nomen: true, regexp: true, bitwise: true, browser: true, forin: true, maxerr: 100, indent: 4 */

var fluid_1_5 = fluid_1_5 || {};
var fluid = fluid || fluid_1_5;

(function ($, fluid) {

    // $().fluid("selectable", args)
    // $().fluid("selectable".that()
    // $().fluid("pager.pagerBar", args)
    // $().fluid("reorderer", options)

/** Create a "bridge" from code written in the Fluid standard "that-ist" style,
 *  to the standard JQuery UI plugin architecture specified at http://docs.jquery.com/UI/Guidelines .
 *  Every Fluid component corresponding to the top-level standard signature (JQueryable, options)
 *  will automatically convert idiomatically to the JQuery UI standard via this adapter. 
 *  Any return value which is a primitive or array type will become the return value
 *  of the "bridged" function - however, where this function returns a general hash
 *  (object) this is interpreted as forming part of the Fluid "return that" pattern,
 *  and the function will instead be bridged to "return this" as per JQuery standard,
 *  permitting chaining to occur. However, as a courtesy, the particular "this" returned
 *  will be augmented with a function that() which will allow the original return
 *  value to be retrieved if desired.
 *  @param {String} name The name under which the "plugin space" is to be injected into
 *  JQuery
 *  @param {Object} peer The root of the namespace corresponding to the peer object.
 */

    fluid.thatistBridge = function (name, peer) {

        var togo = function(funcname) {
            var segs = funcname.split(".");
            var move = peer;
            for (var i = 0; i < segs.length; ++i) {
                move = move[segs[i]];
            }
            var args = [this];
            if (arguments.length === 2) {
                args = args.concat($.makeArray(arguments[1]));
            }
            var ret = move.apply(null, args);
            this.that = function() {
                return ret;
            }
            var type = typeof(ret);
            return !ret || type === "string" || type === "number" || type === "boolean"
              || ret && ret.length !== undefined? ret: this;
        };
        $.fn[name] = togo;
        return togo;
    };

    fluid.thatistBridge("fluid", fluid);
    fluid.thatistBridge("fluid_1_5", fluid_1_5);

/*************************************************************************
 * Tabindex normalization - compensate for browser differences in naming
 * and function of "tabindex" attribute and tabbing order.
 */

    // -- Private functions --
    
    
    var normalizeTabindexName = function() {
        return $.browser.msie ? "tabIndex" : "tabindex";
    };

    var canHaveDefaultTabindex = function(elements) {
       if (elements.length <= 0) {
           return false;
       }

       return $(elements[0]).is("a, input, button, select, area, textarea, object");
    };
    
    var getValue = function(elements) {
        if (elements.length <= 0) {
            return undefined;
        }

        if (!fluid.tabindex.hasAttr(elements)) {
            return canHaveDefaultTabindex(elements) ? Number(0) : undefined;
        }

        // Get the attribute and return it as a number value.
        var value = elements.attr(normalizeTabindexName());
        return Number(value);
    };

    var setValue = function(elements, toIndex) {
        return elements.each(function(i, item) {
            $(item).attr(normalizeTabindexName(), toIndex);
        });
    };
    
    // -- Public API --
    
    /**
     * Gets the value of the tabindex attribute for the first item, or sets the tabindex value of all elements
     * if toIndex is specified.
     * 
     * @param {String|Number} toIndex
     */
    fluid.tabindex = function(target, toIndex) {
        target = $(target);
        if (toIndex !== null && toIndex !== undefined) {
            return setValue(target, toIndex);
        } else {
            return getValue(target);
        }
    };

    /**
     * Removes the tabindex attribute altogether from each element.
     */
    fluid.tabindex.remove = function(target) {
        target = $(target);
        return target.each(function(i, item) {
            $(item).removeAttr(normalizeTabindexName());
        });
    };

    /**
     * Determines if an element actually has a tabindex attribute present.
     */
    fluid.tabindex.hasAttr = function(target) {
        target = $(target);
        if (target.length <= 0) {
            return false;
        }
        var togo = target.map(
            function() {
                var attributeNode = this.getAttributeNode(normalizeTabindexName());
                return attributeNode ? attributeNode.specified : false;
            }
            );
        return togo.length === 1? togo[0] : togo;
    };

    /**
     * Determines if an element either has a tabindex attribute or is naturally tab-focussable.
     */
    fluid.tabindex.has = function(target) {
        target = $(target);
        return fluid.tabindex.hasAttr(target) || canHaveDefaultTabindex(target);
    };

    // Keyboard navigation
    // Public, static constants needed by the rest of the library.
    fluid.a11y = $.a11y || {};

    fluid.a11y.orientation = {
        HORIZONTAL: 0,
        VERTICAL: 1,
        BOTH: 2
    };

    var UP_DOWN_KEYMAP = {
        next: $.ui.keyCode.DOWN,
        previous: $.ui.keyCode.UP
    };

    var LEFT_RIGHT_KEYMAP = {
        next: $.ui.keyCode.RIGHT,
        previous: $.ui.keyCode.LEFT
    };

    // Private functions.
    var unwrap = function(element) {
        return element.jquery ? element[0] : element; // Unwrap the element if it's a jQuery.
    };


    var makeElementsTabFocussable = function(elements) {
        // If each element doesn't have a tabindex, or has one set to a negative value, set it to 0.
        elements.each(function(idx, item) {
            item = $(item);
            if (!item.fluid("tabindex.has") || item.fluid("tabindex") < 0) {
                item.fluid("tabindex", 0);
            }
        });
    };

    // Public API.
    /**
     * Makes all matched elements available in the tab order by setting their tabindices to "0".
     */
    fluid.tabbable = function(target) {
        target = $(target);
        makeElementsTabFocussable(target);
    };

    /*********************************************************************** 
     * Selectable functionality - geometrising a set of nodes such that they
     * can be navigated (by setting focus) using a set of directional keys
     */

    var CONTEXT_KEY = "selectionContext";
    var NO_SELECTION = -32768;

    var cleanUpWhenLeavingContainer = function(selectionContext) {
        if (selectionContext.activeItemIndex !== NO_SELECTION) {
            if (selectionContext.options.onLeaveContainer) {
                selectionContext.options.onLeaveContainer(
                  selectionContext.selectables[selectionContext.activeItemIndex]);
            } else if (selectionContext.options.onUnselect) {
                selectionContext.options.onUnselect(
                selectionContext.selectables[selectionContext.activeItemIndex]);
            }
        }

        if (!selectionContext.options.rememberSelectionState) {
            selectionContext.activeItemIndex = NO_SELECTION;
        }
    };

    /**
     * Does the work of selecting an element and delegating to the client handler.
     */
    var drawSelection = function(elementToSelect, handler) {
        if (handler) {
            handler(elementToSelect);
        }
    };

    /**
     * Does does the work of unselecting an element and delegating to the client handler.
     */
    var eraseSelection = function(selectedElement, handler) {
        if (handler && selectedElement) {
            handler(selectedElement);
        }
    };

    var unselectElement = function(selectedElement, selectionContext) {
        eraseSelection(selectedElement, selectionContext.options.onUnselect);
    };

    var selectElement = function(elementToSelect, selectionContext) {
        // It's possible that we're being called programmatically, in which case we should clear any previous selection.
        unselectElement(selectionContext.selectedElement(), selectionContext);

        elementToSelect = unwrap(elementToSelect);
        var newIndex = selectionContext.selectables.index(elementToSelect);

        // Next check if the element is a known selectable. If not, do nothing.
        if (newIndex === -1) {
           return;
        }

        // Select the new element.
        selectionContext.activeItemIndex = newIndex;
        drawSelection(elementToSelect, selectionContext.options.onSelect);
    };

    var selectableFocusHandler = function(selectionContext) {
        return function(evt) {
            // FLUID-3590: newer browsers (FF 3.6, Webkit 4) have a form of "bug" in that they will go bananas
            // on attempting to move focus off an element which has tabindex dynamically set to -1.
            $(evt.target).fluid("tabindex", 0);
            selectElement(evt.target, selectionContext);

            // Force focus not to bubble on some browsers.
            return evt.stopPropagation();
        };
    };

    var selectableBlurHandler = function(selectionContext) {
        return function(evt) {
            $(evt.target).fluid("tabindex", selectionContext.options.selectablesTabindex);
            unselectElement(evt.target, selectionContext);

            // Force blur not to bubble on some browsers.
            return evt.stopPropagation();
        };
    };

    var reifyIndex = function(sc_that) {
        var elements = sc_that.selectables;
        if (sc_that.activeItemIndex >= elements.length) {
            sc_that.activeItemIndex = 0;
        }
        if (sc_that.activeItemIndex < 0 && sc_that.activeItemIndex !== NO_SELECTION) {
            sc_that.activeItemIndex = elements.length - 1;
        }
        if (sc_that.activeItemIndex >= 0) {
            fluid.focus(elements[sc_that.activeItemIndex]);
        }
    };

    var prepareShift = function(selectionContext) {
        // FLUID-3590: FF 3.6 and Safari 4.x won't fire blur() when programmatically moving focus.
        var selElm = selectionContext.selectedElement();
        if (selElm) {
            fluid.blur(selElm);
        }

        unselectElement(selectionContext.selectedElement(), selectionContext);
        if (selectionContext.activeItemIndex === NO_SELECTION) {
          selectionContext.activeItemIndex = -1;
        }
    };

    var focusNextElement = function(selectionContext) {
        prepareShift(selectionContext);
        ++selectionContext.activeItemIndex;
        reifyIndex(selectionContext);
    };

    var focusPreviousElement = function(selectionContext) {
        prepareShift(selectionContext);
        --selectionContext.activeItemIndex;
        reifyIndex(selectionContext);
    };

    var arrowKeyHandler = function(selectionContext, keyMap, userHandlers) {
        return function(evt) {
            if (evt.which === keyMap.next) {
                focusNextElement(selectionContext);
                evt.preventDefault();
            } else if (evt.which === keyMap.previous) {
                focusPreviousElement(selectionContext);
                evt.preventDefault();
            }
        };
    };

    var getKeyMapForDirection = function(direction) {
        // Determine the appropriate mapping for next and previous based on the specified direction.
        var keyMap;
        if (direction === fluid.a11y.orientation.HORIZONTAL) {
            keyMap = LEFT_RIGHT_KEYMAP;
        } 
        else if (direction === fluid.a11y.orientation.VERTICAL) {
            // Assume vertical in any other case.
            keyMap = UP_DOWN_KEYMAP;
        }

        return keyMap;
    };

    var tabKeyHandler = function(selectionContext) {
        return function(evt) {
            if (evt.which !== $.ui.keyCode.TAB) {
                return;
            }
            cleanUpWhenLeavingContainer(selectionContext);

            // Catch Shift-Tab and note that focus is on its way out of the container.
            if (evt.shiftKey) {
                selectionContext.focusIsLeavingContainer = true;
            }
        };
    };

    var containerFocusHandler = function(selectionContext) {
        return function(evt) {
            var shouldOrig = selectionContext.options.autoSelectFirstItem;
            var shouldSelect = typeof(shouldOrig) === "function" ? 
                 shouldOrig() : shouldOrig;

            // Override the autoselection if we're on the way out of the container.
            if (selectionContext.focusIsLeavingContainer) {
                shouldSelect = false;
            }

            // This target check works around the fact that sometimes focus bubbles, even though it shouldn't.
            if (shouldSelect && evt.target === selectionContext.container.get(0)) {
                if (selectionContext.activeItemIndex === NO_SELECTION) {
                    selectionContext.activeItemIndex = 0;
                }
                fluid.focus(selectionContext.selectables[selectionContext.activeItemIndex]);
            }

           // Force focus not to bubble on some browsers.
           return evt.stopPropagation();
        };
    };

    var containerBlurHandler = function(selectionContext) {
        return function(evt) {
            selectionContext.focusIsLeavingContainer = false;

            // Force blur not to bubble on some browsers.
            return evt.stopPropagation();
        };
    };

    var makeElementsSelectable = function(container, defaults, userOptions) {

        var options = $.extend(true, {}, defaults, userOptions);

        var keyMap = getKeyMapForDirection(options.direction);

        var selectableElements = options.selectableElements? options.selectableElements :
              container.find(options.selectableSelector);
          
        // Context stores the currently active item(undefined to start) and list of selectables.
        var that = {
            container: container,
            activeItemIndex: NO_SELECTION,
            selectables: selectableElements,
            focusIsLeavingContainer: false,
            options: options
        };

        that.selectablesUpdated = function(focusedItem) {
          // Remove selectables from the tab order and add focus/blur handlers
            if (typeof(that.options.selectablesTabindex) === "number") {
                that.selectables.fluid("tabindex", that.options.selectablesTabindex);
            }
            that.selectables.unbind("focus." + CONTEXT_KEY);
            that.selectables.unbind("blur." + CONTEXT_KEY);
            that.selectables.bind("focus."+ CONTEXT_KEY, selectableFocusHandler(that));
            that.selectables.bind("blur." + CONTEXT_KEY, selectableBlurHandler(that));
            if (keyMap && that.options.noBubbleListeners) {
                that.selectables.unbind("keydown."+CONTEXT_KEY);
                that.selectables.bind("keydown."+CONTEXT_KEY, arrowKeyHandler(that, keyMap));
            }
            if (focusedItem) {
                selectElement(focusedItem, that);
            }
            else {
                reifyIndex(that);
            }
        };

        that.refresh = function() {
            if (!that.options.selectableSelector) {
                throw("Cannot refresh selectable context which was not initialised by a selector");
            }
            that.selectables = container.find(options.selectableSelector);
            that.selectablesUpdated();
        };
        
        that.selectedElement = function() {
            return that.activeItemIndex < 0? null : that.selectables[that.activeItemIndex];
        };
        
        // Add various handlers to the container.
        if (keyMap && !that.options.noBubbleListeners) {
            container.keydown(arrowKeyHandler(that, keyMap));
        }
        container.keydown(tabKeyHandler(that));
        container.focus(containerFocusHandler(that));
        container.blur(containerBlurHandler(that));
        
        that.selectablesUpdated();

        return that;
    };

    /**
     * Makes all matched elements selectable with the arrow keys.
     * Supply your own handlers object with onSelect: and onUnselect: properties for custom behaviour.
     * Options provide configurability, including direction: and autoSelectFirstItem:
     * Currently supported directions are jQuery.a11y.directions.HORIZONTAL and VERTICAL.
     */
    fluid.selectable = function(target, options) {
        target = $(target);
        var that = makeElementsSelectable(target, fluid.selectable.defaults, options);
        fluid.setScopedData(target, CONTEXT_KEY, that);
        return that;
    };

    /**
     * Selects the specified element.
     */
    fluid.selectable.select = function(target, toSelect) {
        fluid.focus(toSelect);
    };

    /**
     * Selects the next matched element.
     */
    fluid.selectable.selectNext = function(target) {
        target = $(target);
        focusNextElement(fluid.getScopedData(target, CONTEXT_KEY));
    };

    /**
     * Selects the previous matched element.
     */
    fluid.selectable.selectPrevious = function(target) {
        target = $(target);
        focusPreviousElement(fluid.getScopedData(target, CONTEXT_KEY));
    };

    /**
     * Returns the currently selected item wrapped as a jQuery object.
     */
    fluid.selectable.currentSelection = function(target) {
        target = $(target);
        var that = fluid.getScopedData(target, CONTEXT_KEY);
        return $(that.selectedElement());
    };

    fluid.selectable.defaults = {
        direction: fluid.a11y.orientation.VERTICAL,
        selectablesTabindex: -1,
        autoSelectFirstItem: true,
        rememberSelectionState: true,
        selectableSelector: ".selectable",
        selectableElements: null,
        onSelect: null,
        onUnselect: null,
        onLeaveContainer: null
    };

    /********************************************************************
     *  Activation functionality - declaratively associating actions with 
     * a set of keyboard bindings.
     */

    var checkForModifier = function(binding, evt) {
        // If no modifier was specified, just return true.
        if (!binding.modifier) {
            return true;
        }

        var modifierKey = binding.modifier;
        var isCtrlKeyPresent = modifierKey && evt.ctrlKey;
        var isAltKeyPresent = modifierKey && evt.altKey;
        var isShiftKeyPresent = modifierKey && evt.shiftKey;

        return isCtrlKeyPresent || isAltKeyPresent || isShiftKeyPresent;
    };

    /** Constructs a raw "keydown"-facing handler, given a binding entry. This
     *  checks whether the key event genuinely triggers the event and forwards it
     *  to any "activateHandler" registered in the binding. 
     */
    var makeActivationHandler = function(binding) {
        return function(evt) {
            var target = evt.target;
            if (!fluid.enabled(evt.target)) {
                return;
            }
// The following 'if' clause works in the real world, but there's a bug in the jQuery simulation
// that causes keyboard simulation to fail in Safari, causing our tests to fail:
//     http://ui.jquery.com/bugs/ticket/3229
// The replacement 'if' clause works around this bug.
// When this issue is resolved, we should revert to the original clause.
//            if (evt.which === binding.key && binding.activateHandler && checkForModifier(binding, evt)) {
            var code = evt.which? evt.which : evt.keyCode;
            if (code === binding.key && binding.activateHandler && checkForModifier(binding, evt)) {
                var event = $.Event("fluid-activate");
                $(evt.target).trigger(event, [binding.activateHandler]);
                if (event.isDefaultPrevented()) {
                    evt.preventDefault();
                }
            }
        };
    };

    var makeElementsActivatable = function(elements, onActivateHandler, defaultKeys, options) {
        // Create bindings for each default key.
        var bindings = [];
        $(defaultKeys).each(function(index, key) {
            bindings.push({
                modifier: null,
                key: key,
                activateHandler: onActivateHandler
            });
        });

        // Merge with any additional key bindings.
        if (options && options.additionalBindings) {
            bindings = bindings.concat(options.additionalBindings);
        }

        fluid.initEnablement(elements);

        // Add listeners for each key binding.
        for (var i = 0; i < bindings.length; ++ i) {
            var binding = bindings[i];
            elements.keydown(makeActivationHandler(binding));
        }
        elements.bind("fluid-activate", function(evt, handler) {
            handler = handler || onActivateHandler;
            return handler? handler(evt): null;
        });
    };

    /**
     * Makes all matched elements activatable with the Space and Enter keys.
     * Provide your own handler function for custom behaviour.
     * Options allow you to provide a list of additionalActivationKeys.
     */
    fluid.activatable = function(target, fn, options) {
        target = $(target);
        makeElementsActivatable(target, fn, fluid.activatable.defaults.keys, options);
    };

    /**
     * Activates the specified element.
     */
    fluid.activate = function(target) {
        $(target).trigger("fluid-activate");
    };

    // Public Defaults.
    fluid.activatable.defaults = {
        keys: [$.ui.keyCode.ENTER, $.ui.keyCode.SPACE]
    };

  
  })(jQuery, fluid_1_5);
/*
Copyright 2010-2011 Lucendo Development Ltd.
Copyright 2010-2011 OCAD University

Licensed under the Educational Community License (ECL), Version 2.0 or the New
BSD license. You may not use this file except in compliance with one these
Licenses.

You may obtain a copy of the ECL 2.0 License and BSD License at
https://github.com/fluid-project/infusion/raw/master/Infusion-LICENSE.txt
*/

/** This file contains functions which depend on the presence of a DOM document
 *  and which depend on the contents of Fluid.js **/

// Declare dependencies
/*global fluid_1_5:true, jQuery*/

// JSLint options 
/*jslint white: true, funcinvoke: true, undef: true, newcap: true, nomen: true, regexp: true, bitwise: true, browser: true, forin: true, maxerr: 100, indent: 4 */

var fluid_1_5 = fluid_1_5 || {};

(function ($, fluid) {
    
    fluid.defaults("fluid.viewComponent", {
        gradeNames: ["fluid.littleComponent", "fluid.modelComponent", "fluid.eventedComponent"],
        initFunction: "fluid.initView",
        argumentMap: {
            container: 0,
            options: 1
        }
    });


    // unsupported, NON-API function
    // NOTE: this function represents a temporary strategy until we have more integrated IoC debugging.
    // It preserves the current framework behaviour for the 1.4 release, but provides a more informative
    // diagnostic - in fact, it is perfectly acceptable for a component's creator to return no value and
    // the failure is really in assumptions in fluid.initComponent. Revisit this issue for 1.5
    fluid.diagnoseFailedView = function (componentName, that, options, args) {
        if (!that && fluid.hasGrade(options, "fluid.viewComponent")) {
            var container = fluid.wrap(args[1]);
            var message1 = "Instantiation of autoInit component with type " + componentName + " failed, since ";
            if (container.length === 0) {
                fluid.fail(message1 + "selector \"", args[1], "\" did not match any markup in the document");
            } else {
                fluid.fail(message1 + " component creator function did not return a value");
            }  
        }  
    };
    
    fluid.checkTryCatchParameter = function () {
        var location = window.location || { search: "", protocol: "file:" };
        var GETParams = location.search.slice(1).split('&');
        return fluid.contains(GETParams, "notrycatch");
    };
    
    fluid.notrycatch = fluid.checkTryCatchParameter();

   
    /**
     * Wraps an object in a jQuery if it isn't already one. This function is useful since
     * it ensures to wrap a null or otherwise falsy argument to itself, rather than the
     * often unhelpful jQuery default of returning the overall document node.
     * 
     * @param {Object} obj the object to wrap in a jQuery
     * @param {jQuery} userJQuery the jQuery object to use for the wrapping, optional - use the current jQuery if absent
     */
    fluid.wrap = function (obj, userJQuery) {
        userJQuery = userJQuery || $;
        return ((!obj || obj.jquery) ? obj : userJQuery(obj)); 
    };
    
    /**
     * If obj is a jQuery, this function will return the first DOM element within it.
     * 
     * @param {jQuery} obj the jQuery instance to unwrap into a pure DOM element
     */
    fluid.unwrap = function (obj) {
        return obj && obj.jquery && obj.length === 1 ? obj[0] : obj; // Unwrap the element if it's a jQuery.
    };
    
    /**
     * Fetches a single container element and returns it as a jQuery.
     * 
     * @param {String||jQuery||element} containerSpec an id string, a single-element jQuery, or a DOM element specifying a unique container
     * @param {Boolean} fallible <code>true</code> if an empty container is to be reported as a valid condition
     * @return a single-element jQuery of container
     */
    fluid.container = function (containerSpec, fallible, userJQuery) {
        if (userJQuery) {
            containerSpec = fluid.unwrap(containerSpec);
        }
        var container = fluid.wrap(containerSpec, userJQuery);
        if (fallible && (!container || container.length === 0)) {
            return null;
        }
        
        // Throw an exception if we've got more or less than one element.
        if (!container || !container.jquery || container.length !== 1) {
            if (typeof (containerSpec) !== "string") {
                containerSpec = container.selector;
            }
            var count = container.length !== undefined ? container.length : 0;
            fluid.fail((count > 1 ? "More than one (" + count + ") container elements were"
                    : "No container element was") + " found for selector " + containerSpec);
        }
        if (!fluid.isDOMNode(container[0])) {
            fluid.fail("fluid.container was supplied a non-jQueryable element");  
        }
        
        return container;
    };
    
    /**
     * Creates a new DOM Binder instance, used to locate elements in the DOM by name.
     * 
     * @param {Object} container the root element in which to locate named elements
     * @param {Object} selectors a collection of named jQuery selectors
     */
    fluid.createDomBinder = function (container, selectors) {
        var cache = {}, that = {};
        var userJQuery = container.constructor;
        
        function cacheKey(name, thisContainer) {
            return fluid.allocateSimpleId(thisContainer) + "-" + name;
        }

        function record(name, thisContainer, result) {
            cache[cacheKey(name, thisContainer)] = result;
        }

        that.locate = function (name, localContainer) {
            var selector, thisContainer, togo;
            
            selector = selectors[name];
            thisContainer = localContainer ? localContainer : container;
            if (!thisContainer) {
                fluid.fail("DOM binder invoked for selector " + name + " without container");
            }

            if (!selector) {
                return thisContainer;
            }

            if (typeof (selector) === "function") {
                togo = userJQuery(selector.call(null, fluid.unwrap(thisContainer)));
            } else {
                togo = userJQuery(selector, thisContainer);
            }
            if (togo.get(0) === document) {
                togo = [];
            }
            if (!togo.selector) {
                togo.selector = selector;
                togo.context = thisContainer;
            }
            togo.selectorName = name;
            record(name, thisContainer, togo);
            return togo;
        };
        that.fastLocate = function (name, localContainer) {
            var thisContainer = localContainer ? localContainer : container;
            var key = cacheKey(name, thisContainer);
            var togo = cache[key];
            return togo ? togo : that.locate(name, localContainer);
        };
        that.clear = function () {
            cache = {};
        };
        that.refresh = function (names, localContainer) {
            var thisContainer = localContainer ? localContainer : container;
            if (typeof names === "string") {
                names = [names];
            }
            if (thisContainer.length === undefined) {
                thisContainer = [thisContainer];
            }
            for (var i = 0; i < names.length; ++i) {
                for (var j = 0; j < thisContainer.length; ++j) {
                    that.locate(names[i], thisContainer[j]);
                }
            }
        };
        that.resolvePathSegment = that.locate;
        
        return that;
    };
    
    /** Expect that jQuery selector query has resulted in a non-empty set of 
     * results. If none are found, this function will fail with a diagnostic message, 
     * with the supplied message prepended.
     */
    fluid.expectFilledSelector = function (result, message) {
        if (result && result.length === 0 && result.jquery) {
            fluid.fail(message + ": selector \"" + result.selector + "\" with name " + result.selectorName +
                       " returned no results in context " + fluid.dumpEl(result.context));
        }
    };
    
    /** 
     * The central initialiation method called as the first act of every Fluid
     * component. This function automatically merges user options with defaults,
     * attaches a DOM Binder to the instance, and configures events.
     * 
     * @param {String} componentName The unique "name" of the component, which will be used
     * to fetch the default options from store. By recommendation, this should be the global
     * name of the component's creator function.
     * @param {jQueryable} container A specifier for the single root "container node" in the
     * DOM which will house all the markup for this component.
     * @param {Object} userOptions The configuration options for this component.
     */
     // 4th argument is NOT SUPPORTED, see comments for initLittleComponent
    fluid.initView = function (componentName, containerSpec, userOptions, localOptions) {
        var container = fluid.container(containerSpec, true);
        fluid.expectFilledSelector(container, "Error instantiating component with name \"" + componentName);
        if (!container) {
            return null;
        }
        var that = fluid.initLittleComponent(componentName, userOptions, localOptions || {gradeNames: ["fluid.viewComponent"]});
        var userJQuery = that.options.jQuery; // Do it a second time to correct for jQuery injection
        if (userJQuery) {
            container = fluid.container(containerSpec, true, userJQuery);
        }
        fluid.log("Constructing view component " + componentName + " with container " + container.constructor.expando + 
            (userJQuery ? " user jQuery " + userJQuery.expando : "") + " env: " + $.expando);
        that.container = container;
        fluid.initDomBinder(that);

        return that;
    };
    
    /**
     * Creates a new DOM Binder instance for the specified component and mixes it in.
     * 
     * @param {Object} that the component instance to attach the new DOM Binder to
     */
    fluid.initDomBinder = function (that) {
        that.dom = fluid.createDomBinder(that.container, that.options.selectors);
        that.locate = that.dom.locate;      
    };

    // DOM Utilities.
    
    /**
     * Finds the nearest ancestor of the element that passes the test
     * @param {Element} element DOM element
     * @param {Function} test A function which takes an element as a parameter and return true or false for some test
     */
    fluid.findAncestor = function (element, test) {
        element = fluid.unwrap(element);
        while (element) {
            if (test(element)) {
                return element;
            }
            element = element.parentNode;
        }
    };
    
    /**
     * Returns a jQuery object given the id of a DOM node. In the case the element
     * is not found, will return an empty list.
     */
    fluid.jById = function (id, dokkument) {
        dokkument = dokkument && dokkument.nodeType === 9 ? dokkument : document;
        var element = fluid.byId(id, dokkument);
        var togo = element ? $(element) : [];
        togo.selector = "#" + id;
        togo.context = dokkument;
        return togo;
    };
    
    /**
     * Returns an DOM element quickly, given an id
     * 
     * @param {Object} id the id of the DOM node to find
     * @param {Document} dokkument the document in which it is to be found (if left empty, use the current document)
     * @return The DOM element with this id, or null, if none exists in the document.
     */
    fluid.byId = function (id, dokkument) {
        dokkument = dokkument && dokkument.nodeType === 9 ? dokkument : document;
        var el = dokkument.getElementById(id);
        if (el) {
        // Use element id property here rather than attribute, to work around FLUID-3953
            if (el.id !== id) {
                fluid.fail("Problem in document structure - picked up element " +
                    fluid.dumpEl(el) + " for id " + id +
                    " without this id - most likely the element has a name which conflicts with this id");
            }
            return el;
        } else {
            return null;
        }
    };
    
    /**
     * Returns the id attribute from a jQuery or pure DOM element.
     * 
     * @param {jQuery||Element} element the element to return the id attribute for
     */
    fluid.getId = function (element) {
        return fluid.unwrap(element).id;
    };
    
    /** 
     * Allocate an id to the supplied element if it has none already, by a simple
     * scheme resulting in ids "fluid-id-nnnn" where nnnn is an increasing integer.
     */
    
    fluid.allocateSimpleId = function (element) {
        var simpleId = "fluid-id-" + fluid.allocateGuid();
        if (!element) {
            return simpleId;
        }
        element = fluid.unwrap(element);
        if (!element.id) {
            element.id = simpleId;
        }
        return element.id;
    };

    fluid.defaults("fluid.ariaLabeller", {
        labelAttribute: "aria-label",
        liveRegionMarkup: "<div class=\"liveRegion fl-offScreen-hidden\" aria-live=\"polite\"></div>",
        liveRegionId: "fluid-ariaLabeller-liveRegion",
        events: {
            generateLiveElement: "unicast"
        },
        listeners: {
            generateLiveElement: "fluid.ariaLabeller.generateLiveElement"
        }
    });
 
    fluid.ariaLabeller = function (element, options) {
        var that = fluid.initView("fluid.ariaLabeller", element, options);

        that.update = function (newOptions) {
            newOptions = newOptions || that.options;
            that.container.attr(that.options.labelAttribute, newOptions.text);
            if (newOptions.dynamicLabel) {
                var live = fluid.jById(that.options.liveRegionId); 
                if (live.length === 0) {
                    live = that.events.generateLiveElement.fire(that);
                }
                live.text(newOptions.text);
            }
        };
        
        that.update();
        return that;
    };
    
    fluid.ariaLabeller.generateLiveElement = function (that) {
        var liveEl = $(that.options.liveRegionMarkup);
        liveEl.prop("id", that.options.liveRegionId);
        $("body").append(liveEl);
        return liveEl;
    };
    
    var LABEL_KEY = "aria-labelling";
    
    fluid.getAriaLabeller = function (element) {
        element = $(element);
        var that = fluid.getScopedData(element, LABEL_KEY);
        return that;      
    };
    
    /** Manages an ARIA-mediated label attached to a given DOM element. An
     * aria-labelledby attribute and target node is fabricated in the document
     * if they do not exist already, and a "little component" is returned exposing a method
     * "update" that allows the text to be updated. */
    
    fluid.updateAriaLabel = function (element, text, options) {
        options = $.extend({}, options || {}, {text: text});
        var that = fluid.getAriaLabeller(element);
        if (!that) {
            that = fluid.ariaLabeller(element, options);
            fluid.setScopedData(element, LABEL_KEY, that);
        } else {
            that.update(options);
        }
        return that;
    };
    
    /** Sets an interation on a target control, which morally manages a "blur" for
     * a possibly composite region.
     * A timed blur listener is set on the control, which waits for a short period of
     * time (options.delay, defaults to 150ms) to discover whether the reason for the 
     * blur interaction is that either a focus or click is being serviced on a nominated
     * set of "exclusions" (options.exclusions, a free hash of elements or jQueries). 
     * If no such event is received within the window, options.handler will be called
     * with the argument "control", to service whatever interaction is required of the
     * blur.
     */
    
    fluid.deadMansBlur = function (control, options) {
        var that = fluid.initLittleComponent("fluid.deadMansBlur", options);
        that.blurPending = false;
        that.lastCancel = 0;
        $(control).bind("focusout", function (event) {
            fluid.log("Starting blur timer for element " + fluid.dumpEl(event.target));
            var now = new Date().getTime();
            fluid.log("back delay: " + (now - that.lastCancel));
            if (now - that.lastCancel > that.options.backDelay) {
                that.blurPending = true;
            }
            setTimeout(function () {
                if (that.blurPending) {
                    that.options.handler(control);
                }
            }, that.options.delay);
        });
        that.canceller = function (event) {
            fluid.log("Cancellation through " + event.type + " on " + fluid.dumpEl(event.target)); 
            that.lastCancel = new Date().getTime();
            that.blurPending = false;
        };
        fluid.each(that.options.exclusions, function (exclusion) {
            exclusion = $(exclusion);
            fluid.each(exclusion, function (excludeEl) {
                $(excludeEl).bind("focusin", that.canceller).
                    bind("fluid-focus", that.canceller).
                    click(that.canceller).mousedown(that.canceller);
    // Mousedown is added for FLUID-4212, as a result of Chrome bug 6759, 14204
            });
        });
        return that;
    };

    fluid.defaults("fluid.deadMansBlur", {
        delay: 150,
        backDelay: 100
    });
    
})(jQuery, fluid_1_5);
/*
Copyright 2011 OCAD University
Copyright 2010-2011 Lucendo Development Ltd.

Licensed under the Educational Community License (ECL), Version 2.0 or the New
BSD license. You may not use this file except in compliance with one these
Licenses.

You may obtain a copy of the ECL 2.0 License and BSD License at
https://github.com/fluid-project/infusion/raw/master/Infusion-LICENSE.txt
*/

// Declare dependencies
/*global fluid_1_5:true, jQuery*/

// JSLint options 
/*jslint white: true, funcinvoke: true, continue: true, elsecatch: true, operator: true, jslintok:true, undef: true, newcap: true, regexp: true, bitwise: true, browser: true, forin: true, maxerr: 100, indent: 4 */

var fluid_1_5 = fluid_1_5 || {};

(function ($, fluid) {

    /** The Fluid "IoC System proper" - resolution of references and 
     * completely automated instantiation of declaratively defined
     * component trees */ 
    
    var inCreationMarker = "__CURRENTLY_IN_CREATION__";
    
    // unsupported, non-API function
    fluid.isFireBreak = function(component) {
        return component.options && component.options["fluid.visitComponents.fireBreak"];
    };
    
    // unsupported, non-API function
    fluid.visitComponentChildren = function(that, visitor, options, up, down) {
        options = options || {};
        for (var name in that) {
            var component = that[name];
            //Every component *should* have an id, but some clients may not yet be compliant
            //if (component && component.typeName && !component.id) {
            //    fluid.fail("No id");
            //}
            if (!component || !component.typeName || (component.id && options.visited && options.visited[component.id])) {continue; }
            if (options.visited) {
                options.visited[component.id] = true;
            }
            if (visitor(component, name, options, up, down)) {
                return true;
            }
            if (!fluid.isFireBreak(component) && !options.flat) {
                fluid.visitComponentChildren(component, visitor, options, up, down + 1);
            }
        }
    };
    
    // thatStack contains an increasing list of MORE SPECIFIC thats.
    var visitComponents = function(instantiator, thatStack, visitor, options) {
        options = options || {
            visited: {},
            flat: true
        };
        var up = 0;
        for (var i = thatStack.length - 1; i >= 0; --i) {
            var that = thatStack[i];
            if (fluid.isFireBreak(that)) {
                return;
            }
            if (that.typeName) {
                options.visited[that.id] = true;
                var path = instantiator.idToPath[that.id] || "";
                var memberName = fluid.pathUtil.getTailPath(path);
                if (visitor(that, memberName, options, 0, 0)) {
                    return;
                }
            }
            if (fluid.visitComponentChildren(that, visitor, options, up, 1)) {
                return;
            }
            ++up;
        }
    };
    
    // An EL segment resolver strategy that will attempt to trigger creation of
    // components that it discovers along the EL path, if they have been defined but not yet
    // constructed. Spring, eat your heart out! Wot no SPR-2048?
    
    function makeGingerStrategy(instantiator, that, thatStack) {
        return function(component, thisSeg) {
            var atval = component[thisSeg];
            if (atval === undefined) {
                var parentPath = instantiator.idToPath[component.id];
                atval = instantiator.pathToComponent[fluid.composePath(parentPath, thisSeg)];
                // if it was not attached to the component, but it is in the instantiator, it MUST be in creation - prepare to fail
                if (atval) {
                    atval[inCreationMarker] = true;
                } 
            }
            if (atval !== undefined) {
                if (atval[inCreationMarker]) {
                    fluid.fail("Component " + fluid.dumpThat(atval) + " at path \"" + thisSeg 
                        + "\" of parent " + fluid.dumpThat(component) + " cannot be used for lookup" 
                        + " since it is still in creation. Please reorganise your dependencies so that they no longer contain circular references");
                }
            }
            else {
                if (fluid.get(component, fluid.path("options", "components", thisSeg, "type"))) {
                    fluid.initDependent(component, thisSeg);
                    atval = component[thisSeg];
                }
            }
            return atval;
        };
    }
    
    // unsupported, non-API function
    fluid.dumpThat = function(that) {
        return "{ typeName: \"" + that.typeName + "\" id: " + that.id + "}";
    };
    
        // unsupported, non-API function
    fluid.dumpThatStack = function(thatStack, instantiator) {
        var togo = fluid.transform(thatStack, function(that) {
            var path = instantiator.idToPath[that.id];
            return fluid.dumpThat(that) + (path? (" - path: " + path) : "");
        });
        return togo.join("\n");
    };

    // Return an array of objects describing the current activity
    // unsupported, non-API function
    fluid.describeActivity = function() {
        return fluid.globalThreadLocal().activityStack || [];
    };
    
    // Execute the supplied function with the specified activity description pushed onto the stack
    // unsupported, non-API function
    fluid.pushActivity = function(func, message) {
        if (!message || fluid.notrycatch) {
            return func();
        }
        var root = fluid.globalThreadLocal();
        if (!root.activityStack) {
            root.activityStack = [];
        }
        var frames = fluid.makeArray(message);
        frames.push("\n");
        frames.unshift("\n");
        root.activityStack = frames.concat(root.activityStack);
        return fluid.tryCatch(func, null, function() {
            root.activityStack = root.activityStack.slice(frames.length);
        });
    };
    
    // Return a function wrapped by the activity of describing its activity
    // unsupported, non-API function
    fluid.wrapActivity = fluid.notrycatch? fluid.identity : function(func, messageSpec) {
        return function() {
            var args = fluid.makeArray(arguments);
            var message = fluid.transform(fluid.makeArray(messageSpec), function(specEl) {
                if (typeof(specEl) === "string" && specEl.indexOf("arguments.") === 0) {
                    var el = specEl.substring("arguments.".length);
                    return fluid.get(args, el);
                }
                else {
                    return specEl;
                }
            });
            return fluid.pushActivity(function() {
                return func.apply(null, args);
            }, message);
        };
    };

    var localRecordExpected = /arguments|options|container/;

    function makeStackFetcher(instantiator, parentThat, localRecord, expandOptions) {
        expandOptions = expandOptions || {};
        var thatStack = instantiator.getFullStack(parentThat);
        var fetchStrategies = [fluid.model.funcResolverStrategy, makeGingerStrategy(instantiator, parentThat, thatStack)]; 
        var fetcher = function(parsed) {
            var context = parsed.context;
            if (context === "instantiator") {
                // special treatment for the current instantiator which used to be discovered as unique in threadLocal
                return instantiator;
            }
            if (localRecord && localRecordExpected.test(context)) {
                var fetched = fluid.get(localRecord[context], parsed.path);
                return (context === "arguments" || expandOptions.direct)? fetched : {
                    marker: context === "options"? fluid.EXPAND : fluid.EXPAND_NOW,
                    value: fetched
                };
            }
            var foundComponent;
            visitComponents(instantiator, thatStack, function(component, name, options, up, down) {
                if (context === name || context === component.typeName || context === component.nickName) {
                    foundComponent = component;
                    if (down > 1) {
                        fluid.log("***WARNING: value resolution for context " + context + " found at depth " + down + ": this may not be supported in future");   
                    }
                    return true; // YOUR VISIT IS AT AN END!!
                }
                if (fluid.get(component, fluid.path("options", "components", context, "type")) && !component[context]) {
                    foundComponent = fluid.get(component, context, {strategies: fetchStrategies});
                    return true;
                }
            });
            if (!foundComponent && parsed.path !== "") {
                var ref = fluid.renderContextReference(parsed);
                fluid.log("Failed to resolve reference " + ref + ": thatStack contains\n" + fluid.dumpThatStack(thatStack, instantiator));
                fluid.fail("Failed to resolve reference " + ref + " - could not match context with name " 
                    + context + " from component leaf of type " + thatStack[thatStack.length - 1].typeName, "\ninstantiator contents: ", instantiator);
            }
            return fluid.get(foundComponent, parsed.path, fetchStrategies);
        };
        return fetcher;
    }
     
    function makeStackResolverOptions(instantiator, parentThat, localRecord, expandOptions) {
        return $.extend(true, {}, fluid.defaults("fluid.resolveEnvironment"), {
            fetcher: makeStackFetcher(instantiator, parentThat, localRecord, expandOptions)
        }); 
    }
    
    // unsupported, non-API function
    fluid.instantiator = function(freeInstantiator) {
        // NB: We may not use the options merging framework itself here, since "withInstantiator" below
        // will blow up, as it tries to resolve the instantiator which we are instantiating *NOW*
        var preThat = {
            options: {
                "fluid.visitComponents.fireBreak": true         
            },
            idToPath: {},
            pathToComponent: {},
            nickName: "instantiator"
        };
        var that = fluid.typeTag("fluid.instantiator");
        that = $.extend(that, preThat);

        that.getThatStack = function(component) {
            var path = that.idToPath[component.id] || "";
            var parsed = fluid.model.parseEL(path);
            var togo = fluid.transform(parsed, function(value, i) {
                var parentPath = fluid.model.composeSegments.apply(null, parsed.slice(0, i + 1));
                return that.pathToComponent[parentPath];    
            });
            var root = that.pathToComponent[""];
            if (root) {
                togo.unshift(root);
            }
            return togo;
        };
        that.getEnvironmentalStack = function() {
            var togo = [fluid.staticEnvironment];
            if (!freeInstantiator) {
                togo.push(fluid.globalThreadLocal());
            }
            return togo;
        };
        that.getFullStack = function(component) {
            var thatStack = component? that.getThatStack(component) : [];
            return that.getEnvironmentalStack().concat(thatStack);
        };
        function recordComponent(component, path) {
            that.idToPath[component.id] = path;
            if (that.pathToComponent[path]) {
                fluid.fail("Error during instantiation - path " + path + " which has just created component " + fluid.dumpThat(component) 
                    + " has already been used for component " + fluid.dumpThat(that.pathToComponent[path]) + " - this is a circular instantiation or other oversight."
                    + " Please clear the component using instantiator.clearComponent() before reusing the path.");
            }
            that.pathToComponent[path] = component;          
        }
        that.recordRoot = function(component) {
            if (component && component.id && !that.pathToComponent[""]) {
                recordComponent(component, "");
            }  
        };
        that.pushUpcomingInstantiation = function(parent, name) {
            that.expectedParent = parent;
            that.expectedName = name;
        };
        that.recordComponent = function(component) {
            if (that.expectedName) {
                that.recordKnownComponent(that.expectedParent, component, that.expectedName);
                delete that.expectedName;
                delete that.expectedParent;
            }
            else {
                that.recordRoot(component);
            }
        };
        that.clearComponent = function(component, name, child, options, noModTree) {
            options = options || {visited: {}, flat: true};
            child = child || component[name];
            fluid.visitComponentChildren(child, function(gchild, gchildname) {
                that.clearComponent(child, gchildname, null, options, noModTree);
            }, options);
            var path = that.idToPath[child.id];
            delete that.idToPath[child.id];
            delete that.pathToComponent[path];
            if (!noModTree) {
                delete component[name];
            }
        };
        that.recordKnownComponent = function(parent, component, name) {
            var parentPath = that.idToPath[parent.id] || "";
            var path = fluid.model.composePath(parentPath, name);
            recordComponent(component, path);
        };
        return that;
    };
    
    fluid.freeInstantiator = fluid.instantiator(true);
    
    // unsupported, non-API function
    fluid.argMapToDemands = function(argMap) {
        var togo = [];
        fluid.each(argMap, function(value, key) {
            togo[value] = "{" + key + "}";  
        });
        return togo;
    };
    
    // unsupported, non-API function
    fluid.makePassArgsSpec = function(initArgs) {
        return fluid.transform(initArgs, function(arg, index) {
            return "{arguments}." + index;
        });
    };
    
    function mergeToMergeAll(options) {
        if (options && options.mergeOptions) {
            options.mergeAllOptions = ["{options}"].concat(fluid.makeArray(options.mergeOptions));
        }
    }
    
    function upgradeMergeOptions(demandspec) {
        mergeToMergeAll(demandspec);
        if (demandspec.mergeAllOptions) {
            if (demandspec.options) {
                fluid.fail("demandspec ", demandspec, 
                    " is invalid - cannot specify literal options together with mergeOptions or mergeAllOptions"); 
            }
            demandspec.options = {
                mergeAllOptions: demandspec.mergeAllOptions
            };
        }
        if (demandspec.options) {
            delete demandspec.options.mergeOptions;
        }
    }
    
    /** Given a concrete argument list and/or options, determine the final concrete
     * "invocation specification" which is coded by the supplied demandspec in the 
     * environment "thatStack" - the return is a package of concrete global function name
     * and argument list which is suitable to be executed directly by fluid.invokeGlobalFunction.
     */
    // unsupported, non-API function
    fluid.embodyDemands = function(instantiator, parentThat, demandspec, initArgs, options) {
        options = options || {};
        
        upgradeMergeOptions(demandspec);
        var oldOptions = fluid.get(options, "componentRecord.options");
        options.componentRecord = $.extend(true, {}, options.componentRecord, 
            fluid.censorKeys(demandspec, ["args", "funcName", "registeredFrom"]));
        var mergeAllZero = fluid.get(options, "componentRecord.options.mergeAllOptions.0");
        if (mergeAllZero === "{options}") {
            fluid.set(options, "componentRecord.options.mergeAllOptions.0", oldOptions);
        }
        
        var demands = fluid.makeArray(demandspec.args);
        var upDefaults = fluid.defaults(demandspec.funcName); // I can SEE into TIME!!
        var argMap = upDefaults? upDefaults.argumentMap : null;
        var inferMap = false;
        if (!argMap && (upDefaults || (options && options.componentRecord)) && !options.passArgs) {
            inferMap = true;
            // infer that it must be a little component if we have any reason to believe it is a component
            if (demands.length < 2) {
                argMap = fluid.rawDefaults("fluid.littleComponent").argumentMap;
            }
            else {
                argMap = {options: demands.length - 1}; // wild guess in the old style
            }
        }
        options = options || {};
        if (demands.length === 0) {
            if (options.componentRecord && argMap) {
                demands = fluid.argMapToDemands(argMap);
            }
            else if (options.passArgs) {
                demands = fluid.makePassArgsSpec(initArgs);
            }
        }
        var localRecord = $.extend({"arguments": initArgs}, fluid.censorKeys(options.componentRecord, ["type"]));
        fluid.each(argMap, function(index, name) {
            if (initArgs.length > 0) {
                localRecord[name] = localRecord["arguments"][index];
            }
            if (demandspec[name] !== undefined && localRecord[name] === undefined) {
                localRecord[name] = demandspec[name];
            }
        });
        mergeToMergeAll(localRecord.options);
        mergeToMergeAll(argMap && demands[argMap.options]);
        var upstreamLocalRecord = $.extend({}, localRecord);
        if (options.componentRecord.options !== undefined) {
            upstreamLocalRecord.options = options.componentRecord.options;
        }
        var expandOptions = makeStackResolverOptions(instantiator, parentThat, localRecord);
        var args = [];
        if (demands) {
            for (var i = 0; i < demands.length; ++i) {
                var arg = demands[i];
                // Weak detection since we cannot guarantee this material has not been copied
                if (fluid.isMarker(arg) && arg.value === fluid.COMPONENT_OPTIONS.value) {
                    arg = "{options}";
                    // Backwards compatibility for non-users of GRADES - last-ditch chance to correct the inference
                    if (inferMap) {
                        argMap = {options: i};
                    } 
                }
                if (typeof(arg) === "string") {
                    if (arg.charAt(0) === "@") {
                        var argpos = arg.substring(1);
                        arg = "{arguments}." + argpos;
                    }
                }
                if (!argMap || argMap.options !== i) {
                    // defer expansion required if it is non-pseudoarguments demands and this argument *is* the options
                    args[i] = fluid.expander.expandLight(arg, expandOptions);
                }
                else { // It is the component options
                    if (arg && typeof(arg) === "object" && !arg.targetTypeName) {
                        arg.targetTypeName = demandspec.funcName;
                    }
                    // ensure to copy the arg since it is an alias of the demand block material (FLUID-4223)
                    // and will be destructively expanded
                    args[i] = {marker: fluid.EXPAND, value: fluid.copy(arg), localRecord: upstreamLocalRecord};
                }
                if (args[i] && fluid.isMarker(args[i].marker, fluid.EXPAND_NOW)) {
                    args[i] = fluid.expander.expandLight(args[i].value, expandOptions);
                }
            }
        }
        else {
            args = initArgs? initArgs : [];
        }

        var togo = {
            args: args,
            funcName: demandspec.funcName
        };
        return togo;
    };
    
    var aliasTable = {};
    
    fluid.alias = function(demandingName, aliasName) {
        if (aliasName) {
            aliasTable[demandingName] = aliasName;
        }
        else {
            return aliasTable[demandingName];
        }
    };
   
    var dependentStore = {};
    
    function searchDemands(demandingName, contextNames) {
        var exist = dependentStore[demandingName] || [];
outer:  for (var i = 0; i < exist.length; ++i) {
            var rec = exist[i];
            for (var j = 0; j < contextNames.length; ++j) {
                if (rec.contexts[j] !== contextNames[j]) {
                    continue outer;
                }
            }
            return rec.spec; // jslint:ok
        }
    }
    
    var isDemandLogging = false;
    fluid.setDemandLogging = function(set) {
        isDemandLogging = set;  
    };
    
    // unsupported, non-API function
    fluid.isDemandLogging = function(demandingNames) {
        return isDemandLogging && fluid.isLogging();
    };
    
    fluid.demands = function(demandingName, contextName, spec) {
        var contextNames = fluid.makeArray(contextName).sort(); 
        if (!spec) {
            return searchDemands(demandingName, contextNames);
        }
        else if (spec.length) {
            spec = {args: spec};
        }
        if (fluid.getCallerInfo && fluid.isDemandLogging()) {
            var callerInfo = fluid.getCallerInfo(5);
            if (callerInfo) {
                spec.registeredFrom = callerInfo;
            }
        }
        var exist = dependentStore[demandingName];
        if (!exist) {
            exist = [];
            dependentStore[demandingName] = exist;
        }
        exist.push({contexts: contextNames, spec: spec});
    };

    // unsupported, non-API function
    fluid.compareDemands = function(speca, specb) {
        var p1 = speca.uncess - specb.uncess;
        return p1 === 0? specb.intersect - speca.intersect : p1;
    };
    
    // unsupported, non-API function
    fluid.locateAllDemands = function(instantiator, parentThat, demandingNames) {
        var demandLogging = fluid.isDemandLogging(demandingNames);
        if (demandLogging) {
            fluid.log("Resolving demands for function names ", demandingNames, " in context of " +
                (parentThat? "component " + parentThat.typeName : "no component"));
        }
        
        var contextNames = {};
        var visited = [];
        var thatStack = instantiator.getFullStack(parentThat);
        visitComponents(instantiator, thatStack, function(component, xname, options, up, down) {
            contextNames[component.typeName] = true;
            visited.push(component);
        });
        if (demandLogging) {
            fluid.log("Components in scope for resolution:\n" + fluid.dumpThatStack(visited, instantiator));  
        }
        var matches = [];
        for (var i = 0; i < demandingNames.length; ++i) {
            var rec = dependentStore[demandingNames[i]] || [];
            for (var j = 0; j < rec.length; ++j) {
                var spec = rec[j];
                var record = {spec: spec, intersect: 0, uncess: 0};
                for (var k = 0; k < spec.contexts.length; ++k) {
                    record[contextNames[spec.contexts[k]]? "intersect" : "uncess"] += 2;
                }
                if (spec.contexts.length === 0) { // allow weak priority for contextless matches
                    record.intersect++;
                }
                // TODO: Potentially more subtle algorithm here - also ambiguity reports  
                matches.push(record); 
            }
        }
        matches.sort(fluid.compareDemands);
        return matches;   
    };

    // unsupported, non-API function
    fluid.locateDemands = function(instantiator, parentThat, demandingNames) {
        var matches = fluid.locateAllDemands(instantiator, parentThat, demandingNames);
        var demandspec = matches.length === 0 || matches[0].intersect === 0? null : matches[0].spec.spec;
        if (fluid.isDemandLogging(demandingNames)) {
            if (demandspec) {
                fluid.log("Located " + matches.length + " potential match" + (matches.length === 1? "" : "es") + ", selected best match with " + matches[0].intersect 
                    + " matched context names: ", demandspec);
            }
            else {
                fluid.log("No matches found for demands, using direct implementation");
            }
        }  
        return demandspec;
    };
    
    /** Determine the appropriate demand specification held in the fluid.demands environment 
     * relative to "thatStack" for the function name(s) funcNames.
     */
    // unsupported, non-API function
    fluid.determineDemands = function (instantiator, parentThat, funcNames) {
        funcNames = fluid.makeArray(funcNames);
        var newFuncName = funcNames[0];
        var demandspec = fluid.locateDemands(instantiator, parentThat, funcNames) || {};
        if (demandspec.funcName) {
            newFuncName = demandspec.funcName;
        }
        
        var aliasTo = fluid.alias(newFuncName);
        
        if (aliasTo) {
            newFuncName = aliasTo;
            fluid.log("Following redirect from function name " + newFuncName + " to " + aliasTo);
            var demandspec2 = fluid.locateDemands(instantiator, parentThat, [aliasTo]);
            if (demandspec2) {
                fluid.each(demandspec2, function(value, key) {
                    if (localRecordExpected.test(key)) {
                        fluid.fail("Error in demands block ", demandspec2, " - content with key \"" + key 
                            + "\" is not supported since this demands block was resolved via an alias from \"" + newFuncName + "\"");
                    }  
                });
                if (demandspec2.funcName) {
                    newFuncName = demandspec2.funcName;
                    fluid.log("Followed final inner demands to function name \"" + newFuncName + "\"");
                }
            }
        }
        
        return fluid.merge(null, {funcName: newFuncName, args: fluid.makeArray(demandspec.args)}, fluid.censorKeys(demandspec, ["funcName", "args"]));
    };
    
    // unsupported, non-API function
    fluid.resolveDemands = function(instantiator, parentThat, funcNames, initArgs, options) {
        var demandspec = fluid.determineDemands(instantiator, parentThat, funcNames);
        return fluid.embodyDemands(instantiator, parentThat, demandspec, initArgs, options);
    };
    
    // TODO: make a *slightly* more performant version of fluid.invoke that perhaps caches the demands
    // after the first successful invocation
    fluid.invoke = function(functionName, args, that, environment) {
        args = fluid.makeArray(args);
        return fluid.withInstantiator(that, function(instantiator) {
            var invokeSpec = fluid.resolveDemands(instantiator, that, functionName, args, {passArgs: true});
            return fluid.invokeGlobalFunction(invokeSpec.funcName, invokeSpec.args, environment);
        });
    };
    
    fluid.invoke = fluid.wrapActivity(fluid.invoke, ["    while invoking function with name \"", "arguments.0", "\" from component", "arguments.2"]); 
    
    /** Make a function which performs only "static redispatch" of the supplied function name - 
     * that is, taking only account of the contents of the "static environment". Since the static
     * environment is assumed to be constant, the dispatch of the call will be evaluated at the
     * time this call is made, as an optimisation.
     */
    
    fluid.makeFreeInvoker = function(functionName, environment) {
        var demandSpec = fluid.determineDemands(fluid.freeInstantiator, null, functionName);
        return function() {
            var invokeSpec = fluid.embodyDemands(fluid.freeInstantiator, null, demandSpec, fluid.makeArray(arguments), {passArgs: true});
            return fluid.invokeGlobalFunction(invokeSpec.funcName, invokeSpec.args, environment);
        };
    };
    
    fluid.makeInvoker = function(instantiator, that, demandspec, functionName, environment) {
        demandspec = demandspec || fluid.determineDemands(instantiator, that, functionName);
        return function() {
            var args = fluid.makeArray(arguments);
            return fluid.pushActivity(function() {
                var invokeSpec = fluid.embodyDemands(instantiator, that, demandspec, args, {passArgs: true});
                return fluid.invokeGlobalFunction(invokeSpec.funcName, invokeSpec.args, environment);
            }, ["    while invoking invoker with name " + functionName + " on component", that]);
        };
    };
    
    fluid.event.listenerEngine = function(eventSpec, callback) {
        var argstruc = {};
        function checkFire() {
            var notall = fluid.find(eventSpec, function(value, key) {
                if (argstruc[key] === undefined) {
                    return true;
                }  
            });
            if (!notall) {
                callback(argstruc);
                fluid.clear(argstruc);
            }
        }
        fluid.each(eventSpec, function(event, eventName) {
            event.addListener(function() {
                argstruc[eventName] = fluid.makeArray(arguments);
                checkFire();
            });
        });
    };
    
    // unsupported, non-API function
    fluid.event.dispatchListener = function(instantiator, that, listener, eventName, eventSpec, indirectArgs) {
        return fluid.wrapActivity(function() {
            listener = fluid.event.resolveListener(listener); // just resolves globals
            var args = indirectArgs? arguments[0] : fluid.makeArray(arguments);
            var demandspec = fluid.determineDemands(instantiator, that, eventName);
            if (demandspec.args.length === 0 && eventSpec.args) {
                demandspec.args = eventSpec.args;
            }
            var resolved = fluid.embodyDemands(instantiator, that, demandspec, args, {passArgs: true, componentOptions: eventSpec}); 
            return listener.apply(null, resolved.args);
        }, [" firing to listener to event named " + eventName + " of component ", that]);
    };
    
    fluid.event.resolveListenerRecord = function(lisrec, that, eventName) {
        return fluid.withInstantiator(that, function(instantiator) {
            var records = fluid.makeArray(lisrec);
            return fluid.transform(records, function(record) {
                if (fluid.isPrimitive(record)) {
                    record = {listener: record};
                }
                var listener = fluid.expandOptions(record.listener, that);
                if (!listener) {
                    fluid.fail("Error in listener record - could not resolve reference " + record.listener + " to a listener or firer. "
                        + "Did you miss out \"events.\" when referring to an event firer?");
                }
                if (listener.typeName === "fluid.event.firer") {
                    listener = listener.fire;
                }
                record.listener = fluid.event.dispatchListener(instantiator, that, listener, eventName, record);
                return record;
            });
        }, [ "    while resolving listener record for event named " + eventName + " for component ", that]); 
    };
    
    fluid.event.expandOneEvent = function(event, that) {
        var origin;
        if (typeof(event) === "string" && event.charAt(0) !== "{") {
            // Special dispensation so we can resolve onto our own events without GINGER WORLD
            origin = that.events[event];
        }
        else {
            origin = fluid.expandOptions(event, that);
        }
        if (!origin || origin.typeName !== "fluid.event.firer") {
            fluid.fail("Error in event specification - could not resolve base event reference ", event, " to an event firer: got ", origin);
        }
        return origin;
    };
    
    fluid.event.expandEvents = function(event, that) {
        return typeof(event) === "string"?
            fluid.event.expandOneEvent(event, that) :
            fluid.transform(event, function(oneEvent) {
                return fluid.event.expandOneEvent(oneEvent, that);
            });
    };
    
    // unsupported, non-API function
    fluid.event.resolveEvent = function(that, eventName, eventSpec) {
        return fluid.withInstantiator(that, function(instantiator) {
            if (typeof(eventSpec) === "string") {
                eventSpec = {event: eventSpec};
            }
            var event = eventSpec.event || eventSpec.events;
            if (!event) {
                fluid.fail("Event specification for event with name " + eventName + " does not include a base event specification: ", eventSpec);
            }
            
            var origin = fluid.event.expandEvents(event, that);

            var isMultiple = origin.typeName !== "fluid.event.firer";
            var isComposite = eventSpec.args || isMultiple;
            // If "event" is not composite, we want to share the listener list and FIRE method with the original
            // If "event" is composite, we need to create a new firer. "composite" includes case where any boiling
            // occurred - this was implemented wrongly in 1.4.
            var firer;
            if (isComposite) {
                firer = fluid.event.getEventFirer(null, null, " [composite] " + fluid.event.nameEvent(that, eventName));
                var dispatcher = fluid.event.dispatchListener(instantiator, that, firer.fire, eventName, eventSpec, isMultiple);
                if (isMultiple) {
                    fluid.event.listenerEngine(origin, dispatcher);
                }
                else {
                    origin.addListener(dispatcher);
                }
            }
            else {
                firer = {typeName: "fluid.event.firer"}; // jslint:ok - already defined
                firer.fire = function () {
                    var outerArgs = fluid.makeArray(arguments);
                    // TODO: this resolution should really be supplied for ALL events!
                    return fluid.withInstantiator(that, function () {
                        return origin.fire.apply(null, outerArgs);
                    }, " firing synthetic event " + eventName, instantiator);
                };
                firer.addListener = function (listener, namespace, predicate, priority) {
                    var dispatcher = fluid.event.dispatchListener(instantiator, that, listener, eventName, eventSpec);
                    origin.addListener(dispatcher, namespace, predicate, priority);
                };
                firer.removeListener = function (listener) {
                    origin.removeListener(listener);
                };
            }
            return firer;
        }, ["    while resolving event with name " + eventName + " attached to component ", that]); 
    };
    
        
    fluid.registerNamespace("fluid.expander");
    
    /** rescue that part of a component's options which should not be subject to
     * options expansion via IoC - this initially consists of "components" and "mergePolicy" 
     * but will be expanded by the set of paths specified as "noexpand" within "mergePolicy" 
     */
    // unsupported, non-API function
    fluid.expander.preserveFromExpansion = function(options) {
        var preserve = {};
        var preserveList = fluid.arrayToHash(["mergePolicy", "mergeAllOptions", "components", "invokers", "events", "listeners", "transformOptions"]);
        fluid.each(options.mergePolicy, function(value, key) {
            if (fluid.mergePolicyIs(value, "noexpand")) {
                preserveList[key] = true;
            }
        });
        fluid.each(preserveList, function(xvalue, path) {
            var pen = fluid.model.getPenultimate(options, path);
            var value = pen.root[pen.last];
            delete pen.root[pen.last];
            fluid.set(preserve, path, value);  
        });
        return {
            restore: function(target) {
                fluid.each(preserveList, function(xvalue, path) {
                    var preserved = fluid.get(preserve, path);
                    if (preserved !== undefined) {
                        fluid.set(target, path, preserved);
                    }
                });
            }
        };
    };
    
    /** Expand a set of component options with respect to a set of "expanders" (essentially only
     *  deferredCall) -  This substitution is destructive since it is assumed that the options are already "live" as the
     *  result of environmental substitutions. Note that options contained inside "components" will not be expanded
     *  by this call directly to avoid linearly increasing expansion depth if this call is occuring as a result of
     *  "initDependents" */
     // TODO: This needs to be integrated with "embodyDemands" above which makes a call to "resolveEnvironment" directly
     // but with very similarly derived options (makeStackResolverOptions)
    fluid.expandOptions = function(args, that, localRecord, outerExpandOptions) {
        if (!args) {
            return args;
        }
        return fluid.withInstantiator(that, function(instantiator) {
            //fluid.log("expandOptions for " + that.typeName + " executing with instantiator " + instantiator.id);
            var expandOptions = makeStackResolverOptions(instantiator, that, localRecord, outerExpandOptions);
            expandOptions.noCopy = true; // It is still possible a model may be fetched even though it is preserved
            var pres;
            if (!fluid.isArrayable(args) && !fluid.isPrimitive(args)) {
                pres = fluid.expander.preserveFromExpansion(args);
            }
            var expanded = fluid.expander.expandLight(args, expandOptions);
            if (pres) {
                pres.restore(expanded);
            }
            return expanded;
        }, ["    while expanding options for component of type " + that.typeName + ": ", that]);
    };
    
    // unsupported, non-API function    
    fluid.locateTransformationRecord = function(that) {
        return fluid.withInstantiator(that, function(instantiator) {
            var matches = fluid.locateAllDemands(instantiator, that, ["fluid.transformOptions"]);
            return fluid.find(matches, function(match) {
                return match.uncess === 0 && fluid.contains(match.spec.contexts, that.typeName)? match.spec.spec : undefined;
            });
        });
    };
    
    // 
    fluid.hashToArray = function(hash) {
        var togo = [];
        fluid.each(hash, function(value, key) {
            togo.push(key);
        });
        return togo;
    };
    
    // unsupported, non-API function    
    fluid.localRecordExpected = ["type", "options", "arguments", "mergeOptions",
        "mergeAllOptions", "createOnEvent", "priority"];
    // unsupported, non-API function    
    fluid.checkComponentRecord = function(defaults, localRecord) {
        var expected = fluid.arrayToHash(fluid.localRecordExpected);
        fluid.each(defaults.argumentMap, function(value, key) {
            expected[key] = true;
        });
        fluid.each(localRecord, function(value, key) {
            if (!expected[key]) {
                fluid.fail("Probable error in subcomponent record - key \"" + key + 
                    "\" found, where the only legal options are " + 
                    fluid.hashToArray(expected).join(", "));
            }  
        });
    };
    
    // unsupported, non-API function
    fluid.expandComponentOptions = function(defaults, userOptions, that) {
        if (userOptions && userOptions.localRecord) {
            fluid.checkComponentRecord(defaults, userOptions.localRecord);
        }
        defaults = fluid.expandOptions(fluid.copy(defaults), that);
        var localRecord = {};
        if (userOptions && userOptions.marker === fluid.EXPAND) {
            // TODO: Somewhat perplexing... the local record itself, by any route we could get here, consists of unexpanded
            // material taken from "componentOptions"
            var localOptions = fluid.get(userOptions, "localRecord.options");
            if (localOptions) {
                if (defaults && defaults.mergePolicy) {
                    localOptions.mergePolicy = defaults.mergePolicy;
                }
                localRecord.options = fluid.expandOptions(localOptions, that);
            }
            localRecord["arguments"] = fluid.get(userOptions, "localRecord.arguments");
            var toExpand = userOptions.value;
            userOptions = fluid.expandOptions(toExpand, that, localRecord, {direct: true});
        }
        localRecord.directOptions = userOptions;
        if (!localRecord.options) {
            // Catch the case where there is no demands block and everything is in the subcomponent record - 
            // in this case, embodyDemands will not construct a localRecord and what the user refers to by "options"
            // is really what we properly call "directOptions".
            localRecord.options = userOptions;
        }
        var mergeOptions = (userOptions && userOptions.mergeAllOptions) || ["{directOptions}"];
        var togo = fluid.transform(mergeOptions, function(path) {
            // Avoid use of expandOptions in simple case to avoid infinite recursion when constructing instantiator
            return path === "{directOptions}"? localRecord.directOptions : fluid.expandOptions(path, that, localRecord, {direct: true}); 
        });
        var transRec = fluid.locateTransformationRecord(that);
        if (transRec) {
            togo[0].transformOptions = transRec.options;
        }
        return [defaults].concat(togo);
    };
    
    fluid.expandComponentOptions = fluid.wrapActivity(fluid.expandComponentOptions, 
        ["    while expanding component options ", "arguments.1.value", " with record ", "arguments.1", " for component ", "arguments.2"]);

   
    // NON-API function 
    fluid.getInstantiators = function() {
        var root = fluid.globalThreadLocal();
        var ins = root["fluid.instantiator"];
        if (!ins) {
            ins = root["fluid.instantiator"] = [];
        }
        return ins;    
    };
    
    // These two are the only functions which touch the instantiator stack
    // NON-API function
    // This function is stateful and MUST NOT be called by client code
    fluid.withInstantiator = function(that, func, message, userInstantiator) {
        var ins = fluid.getInstantiators();
        var oldLength;
        var instantiator = userInstantiator;

        return fluid.pushActivity(function() {
            return fluid.tryCatch(function() {
                if (!instantiator) {
                    if (ins.length === 0) {
                        instantiator = fluid.instantiator();
                        fluid.log("Created new instantiator with id " + instantiator.id + " in order to operate on component " + (that? that.typeName : "[none]"));
                        }
                    else {
                        instantiator = ins[ins.length - 1];
                    }
                }
                ins.push(instantiator);
                oldLength = ins.length;
              
                if (that) {
                    instantiator.recordComponent(that);
                }
                //fluid.log("Instantiator stack +1 to " + instantiator.stackCount + " for " + typeName);
                return func(instantiator);
            }, null, function() {
                if (ins.length !== oldLength) {
                    fluid.fail("Instantiator stack corrupted - old length " + oldLength + " new length " + ins.length);
                }
                if (ins[ins.length - 1] != instantiator) {
                    fluid.fail("Instantiator stack corrupted at stack top - old id " + instantiator.id + " new id " + ins[ins.length-1].id); 
                }
                ins.length--;
                //fluid.log("Instantiator stack -1 to " + instantiator.stackCount + " for " + typeName);
                if (ins.length === 0) {
                    fluid.log("Cleared instantiators (last id " + instantiator.id + ") from threadLocal for end of " + (that? that.typeName : "[none]"));
                }
            });
        }, message);
    };
    
    // The case without the instantiator is from the ginger strategy - this logic is still a little ragged
    fluid.initDependent = function(that, name, userInstantiator, directArgs) {
        if (!that || that[name]) { return; }
        fluid.log("Beginning instantiation of component with name \"" + name + "\" as child of " + fluid.dumpThat(that));
        directArgs = directArgs || [];
        var component = that.options.components[name];
        var instance; // escape to here for debugging purposes
        
        fluid.withInstantiator(that, function(instantiator) {
            if (typeof(component) === "string") {
                that[name] = fluid.expandOptions([component], that)[0]; // TODO: expose more sensible semantic for expandOptions 
            }
            else if (component.type) {
                var invokeSpec = fluid.resolveDemands(instantiator, that, [component.type, name], directArgs, {componentRecord: component});
                instantiator.pushUpcomingInstantiation(that, name);
                fluid.tryCatch(function() {
                    that[inCreationMarker] = true;
                    instance = fluid.initSubcomponentImpl(that, {type: invokeSpec.funcName}, invokeSpec.args);
                    // The existing instantiator record will be provisional, adjust it to take account of the true return
                    // TODO: Instantiator contents are generally extremely incomplete
                    var path = fluid.composePath(instantiator.idToPath[that.id] || "", name);
                    var existing = instantiator.pathToComponent[path];
                    if (existing && existing !== instance) {
                        instantiator.clearComponent(that, name, existing, null, true);
                    }
                    if (instance && instance.typeName && instance.id && instance !== existing) {
                        instantiator.recordKnownComponent(that, instance, name);
                    }
                    that[name] = instance;
                }, null, function() {
                    delete that[inCreationMarker];
                    instantiator.pushUpcomingInstantiation();
                });
            }
            else { 
                that[name] = component;
            }
        }, ["    while instantiating dependent component with name \"" + name + "\" with record ", component, " as child of ", that],
        userInstantiator);
        if (instance) {
            fluid.log("Finished instantiation of component with name \"" + name + "\" and id " + instance.id + " as child of " + fluid.dumpThat(that));
        }
    };
    
    // unsupported, non-API function
    fluid.bindDeferredComponent = function(that, componentName, component, instantiator) {
        var events = fluid.makeArray(component.createOnEvent);
        fluid.each(events, function(eventName) {
            that.events[eventName].addListener(function() {
                fluid.log("Beginning instantiation of deferred component " + componentName + " due to event " + eventName);
                if (that[componentName]) {
                    instantiator.clearComponent(that, componentName);
                }
                fluid.initDependent(that, componentName, instantiator);
            }, null, null, component.priority);
        });
    };
    
    // unsupported, non-API function
    fluid.priorityForComponent = function(component) {
        return component.priority? component.priority : 
            (component.type === "fluid.typeFount" || fluid.hasGrade(fluid.defaults(component.type), "fluid.typeFount"))?
            "first" : undefined;  
    };
    
    fluid.initDependents = function(that) {
        var options = that.options;
        var components = options.components || {};
        var componentSort = {};
        fluid.withInstantiator(that, function(instantiator) {
            fluid.each(components, function(component, name) {
                if (!component.createOnEvent) {
                    var priority = fluid.priorityForComponent(component);
                    componentSort[name] = {key: name, priority: fluid.event.mapPriority(priority, 0)};
                }
                else {
                    fluid.bindDeferredComponent(that, name, component, instantiator);
                }
            });
            var componentList = fluid.event.sortListeners(componentSort);
            fluid.each(componentList, function(entry) {
                fluid.initDependent(that, entry.key);  
            });
            var invokers = options.invokers || {};
            for (var name in invokers) {
                var invokerec = invokers[name];
                var funcName = typeof(invokerec) === "string"? invokerec : null;
                that[name] = fluid.withInstantiator(that, function(instantiator) {
                    fluid.log("Beginning instantiation of invoker with name \"" + name + "\" as child of " + fluid.dumpThat(that));
                    return fluid.makeInvoker(instantiator, that, funcName? null : invokerec, funcName);
                }, ["    while instantiating invoker with name \"" + name + "\" with record ", invokerec, " as child of ", that]); // jslint:ok
                fluid.log("Finished instantiation of invoker with name \"" + name + "\" as child of " + fluid.dumpThat(that)); 
            }
        }, ["    while instantiating dependent components for component " + that.typeName]);
    };   
        
    fluid.staticEnvironment = fluid.typeTag("fluid.staticEnvironment");
    
    fluid.staticEnvironment.environmentClass = fluid.typeTag("fluid.browser");
    
    fluid.globalThreadLocal = fluid.threadLocal(function() {
        return fluid.typeTag("fluid.dynamicEnvironment");
    });
    
    // Although the following two functions are unsupported and not part of the IoC
    // implementation proper, they are still used in the renderer
    // expander as well as in some old-style tests and various places in CSpace.
    
    // unsupported, non-API function
    fluid.withEnvironment = function(envAdd, func, root) {
        root = root || fluid.globalThreadLocal();
        return fluid.tryCatch(function() {
            for (var key in envAdd) {
                root[key] = envAdd[key];
            }
            $.extend(root, envAdd);
            return func();
        }, null, function() {
            for (var key in envAdd) { // jslint:ok duplicate "value"
                delete root[key]; // TODO: users may want a recursive "scoping" model
            }
        });
    };
    
    // unsupported, non-API function  
    fluid.makeEnvironmentFetcher = function(directModel, elResolver, envGetter) {
        envGetter = envGetter || fluid.globalThreadLocal;
        return function(parsed) {
            var env = envGetter();
            return fluid.fetchContextReference(parsed, directModel, env, elResolver);
        };
    };

    // unsupported, non-API function  
    fluid.extractEL = function(string, options) {
        if (options.ELstyle === "ALL") {
            return string;
        }
        else if (options.ELstyle.length === 1) {
            if (string.charAt(0) === options.ELstyle) {
                return string.substring(1);
            }
        }
        else if (options.ELstyle === "${}") {
            var i1 = string.indexOf("${");
            var i2 = string.lastIndexOf("}");
            if (i1 === 0 && i2 !== -1) {
                return string.substring(2, i2);
            }
        }
    };
    
    // unsupported, non-API function
    fluid.extractELWithContext = function(string, options) {
        var EL = fluid.extractEL(string, options);
        if (EL && EL.charAt(0) === "{") {
            return fluid.parseContextReference(EL, 0);
        }
        return EL? {path: EL} : EL;
    };

    fluid.parseContextReference = function(reference, index, delimiter) {
        var endcpos = reference.indexOf("}", index + 1);
        if (endcpos === -1) {
            fluid.fail("Cannot parse context reference \"" + reference + "\": Malformed context reference without }");
        }
        var context = reference.substring(index + 1, endcpos);
        var endpos = delimiter? reference.indexOf(delimiter, endcpos + 1) : reference.length;
        var path = reference.substring(endcpos + 1, endpos);
        if (path.charAt(0) === ".") {
            path = path.substring(1);
        }
        return {context: context, path: path, endpos: endpos};
    };
    
    fluid.renderContextReference = function(parsed) {
        return "{" + parsed.context + "}." + parsed.path;  
    };
    
    fluid.fetchContextReference = function(parsed, directModel, env, elResolver) {
        if (elResolver) {
            parsed = elResolver(parsed, env);
        }
        var base = parsed.context? env[parsed.context] : directModel;
        if (!base) {
            return base;
        }
        return parsed.noDereference? parsed.path : fluid.get(base, parsed.path);
    };
    
    // unsupported, non-API function
    fluid.resolveContextValue = function(string, options) {
        if (options.bareContextRefs && string.charAt(0) === "{") {
            var parsed = fluid.parseContextReference(string, 0);
            return options.fetcher(parsed);        
        }
        else if (options.ELstyle && options.ELstyle !== "${}") {
            var parsed = fluid.extractELWithContext(string, options); // jslint:ok
            if (parsed) {
                return options.fetcher(parsed);
            }
        }
        while (typeof(string) === "string") {
            var i1 = string.indexOf("${");
            var i2 = string.indexOf("}", i1 + 2);
            if (i1 !== -1 && i2 !== -1) {
                var parsed; // jslint:ok
                if (string.charAt(i1 + 2) === "{") {
                    parsed = fluid.parseContextReference(string, i1 + 2, "}");
                    i2 = parsed.endpos;
                }
                else {
                    parsed = {path: string.substring(i1 + 2, i2)};
                }
                var subs = options.fetcher(parsed);
                var all = (i1 === 0 && i2 === string.length - 1); 
                // TODO: test case for all undefined substitution
                if (subs === undefined || subs === null) {
                    return subs;
                }
                string = all? subs : string.substring(0, i1) + subs + string.substring(i2 + 1);
            }
            else {
                break;
            }
        }
        return string;
    };
    
    fluid.resolveContextValue = fluid.wrapActivity(fluid.resolveContextValue, 
        ["    while resolving context value ", "arguments.0"]);
    
    function resolveEnvironmentImpl(obj, options) {
        fluid.guardCircularity(options.seenIds, obj, "expansion", 
             " - please ensure options are not circularly connected, or protect from expansion using the \"noexpand\" policy or expander");
        function recurse(arg) {
            return resolveEnvironmentImpl(arg, options);
        }
        if (typeof(obj) === "string" && !options.noValue) {
            return fluid.resolveContextValue(obj, options);
        }
        else if (fluid.isPrimitive(obj) || obj.nodeType !== undefined || obj.jquery) {
            return obj;
        }
        else if (options.filter) {
            return options.filter(obj, recurse, options);
        }
        else {
            return (options.noCopy? fluid.each : fluid.transform)(obj, function(value, key) {
                return resolveEnvironmentImpl(value, options);
            });
        }
    }
    
    fluid.defaults("fluid.resolveEnvironment", {
        ELstyle:     "${}",
        seenIds:     {},
        bareContextRefs: true
    });
    
    fluid.resolveEnvironment = function(obj, options) {
        // Don't create a component here since this function is itself used in the 
        // component expansion pathway - avoid all expansion in any case to head off FLUID-4301
        options = $.extend({}, fluid.rawDefaults("fluid.resolveEnvironment"), options);
        options.seenIds = {};
        return resolveEnvironmentImpl(obj, options);
    };

    /** "light" expanders, starting with support functions for the "deferredFetcher" expander **/

    fluid.expander.deferredCall = function(target, source, recurse) {
        var expander = source.expander;
        var args = (!expander.args || fluid.isArrayable(expander.args))? expander.args : fluid.makeArray(expander.args);
        args = recurse(args); 
        return fluid.invokeGlobalFunction(expander.func, args);
    };
    
    fluid.deferredCall = fluid.expander.deferredCall; // put in top namespace for convenience
    
    fluid.deferredInvokeCall = function(target, source, recurse) {
        var expander = source.expander;
        var args = (!expander.args || fluid.isArrayable(expander.args))? expander.args : fluid.makeArray(expander.args);
        args = recurse(args);  
        return fluid.invoke(expander.func, args);
    };
    
    // The "noexpand" expander which simply unwraps one level of expansion and ceases.
    fluid.expander.noexpand = function(target, source) {
        return $.extend(target, source.expander.tree);
    };
  
    fluid.noexpand = fluid.expander.noexpand; // TODO: check naming and namespacing
  
    // unsupported, non-API function
    fluid.expander.lightFilter = function (obj, recurse, options) {
        var togo;
        if (fluid.isArrayable(obj)) {
            togo = options.noCopy? obj : [];
            fluid.each(obj, function(value, key) {togo[key] = recurse(value);});
        }
        else {
            togo = options.noCopy? obj : {};
            for (var key in obj) {
                var value = obj[key];
                var expander;
                if (key === "expander" && !(options.expandOnly && options.expandOnly[value.type])) {
                    expander = fluid.getGlobalValue(value.type);  
                    if (expander) {
                        return expander.call(null, togo, obj, recurse, options);
                    }
                }
                if (key !== "expander" || !expander) {
                    togo[key] = recurse(value);
                }
            }
        }
        return options.noCopy? obj : togo;
    };
      
    // unsupported, non-API function
    fluid.expander.expandLight = function (source, expandOptions) {
        var options = $.extend({}, expandOptions);
        options.filter = fluid.expander.lightFilter;
        return fluid.resolveEnvironment(source, options);       
    };
          
})(jQuery, fluid_1_5);
/*
Copyright 2010-2011 OCAD University
Copyright 2010-2011 Lucendo Development Ltd.

Licensed under the Educational Community License (ECL), Version 2.0 or the New
BSD license. You may not use this file except in compliance with one these
Licenses.

You may obtain a copy of the ECL 2.0 License and BSD License at
https://github.com/fluid-project/infusion/raw/master/Infusion-LICENSE.txt
*/

// Declare dependencies
/*global fluid_1_5:true, jQuery*/

// JSLint options 
/*jslint white: true, funcinvoke: true, undef: true, newcap: true, nomen: true, regexp: true, bitwise: true, browser: true, forin: true, maxerr: 100, indent: 4 */

var fluid_1_5 = fluid_1_5 || {};

(function ($, fluid) {

    /** Framework-global caching state for fluid.fetchResources **/

    var resourceCache = {};
  
    var pendingClass = {};
 
    /** Accepts a hash of structures with free keys, where each entry has either
     * href/url or nodeId set - on completion, callback will be called with the populated
     * structure with fetched resource text in the field "resourceText" for each
     * entry. Each structure may contain "options" holding raw options to be forwarded
     * to jQuery.ajax().
     */
  
    fluid.fetchResources = function(resourceSpecs, callback, options) {
        var that = fluid.initLittleComponent("fluid.fetchResources", options);
        that.resourceSpecs = resourceSpecs;
        that.callback = callback;
        that.operate = function() {
            fluid.fetchResources.fetchResourcesImpl(that);
        };
        fluid.each(resourceSpecs, function(resourceSpec, key) {
             resourceSpec.recurseFirer = fluid.event.getEventFirer(null, null, "I/O completion for resource \"" + key + "\"");
             resourceSpec.recurseFirer.addListener(that.operate);
             if (resourceSpec.url && !resourceSpec.href) {
                resourceSpec.href = resourceSpec.url;
             }
        });
        if (that.options.amalgamateClasses) {
            fluid.fetchResources.amalgamateClasses(resourceSpecs, that.options.amalgamateClasses, that.operate);
        }
        that.operate();
        return that;
    };
  
    /*
     * This function is unsupported: It is not really intended for use by implementors.
     */
    // Add "synthetic" elements of *this* resourceSpec list corresponding to any
    // still pending elements matching the PROLEPTICK CLASS SPECIFICATION supplied 
    fluid.fetchResources.amalgamateClasses = function(specs, classes, operator) {
        fluid.each(classes, function(clazz) {
            var pending = pendingClass[clazz];
            fluid.each(pending, function(pendingrec, canon) {
                specs[clazz+"!"+canon] = pendingrec;
                pendingrec.recurseFirer.addListener(operator);
            });
        });
    };
  
    /*
     * This function is unsupported: It is not really intended for use by implementors.
     */
    fluid.fetchResources.timeSuccessCallback = function(resourceSpec) {
        if (resourceSpec.timeSuccess && resourceSpec.options && resourceSpec.options.success) {
            var success = resourceSpec.options.success;
            resourceSpec.options.success = function() {
            var startTime = new Date();
            var ret = success.apply(null, arguments);
            fluid.log("External callback for URL " + resourceSpec.href + " completed - callback time: " + 
                    (new Date().getTime() - startTime.getTime()) + "ms");
            return ret;
            };
        }
    };
    
    // TODO: Integrate punch-through from old Engage implementation
    function canonUrl(url) {
        return url;
    }
    
    fluid.fetchResources.clearResourceCache = function(url) {
        if (url) {
            delete resourceCache[canonUrl(url)];
        }
        else {
            fluid.clear(resourceCache);
        }  
    };
  
    /*
     * This function is unsupported: It is not really intended for use by implementors.
     */
    fluid.fetchResources.handleCachedRequest = function(resourceSpec, response) {
         var canon = canonUrl(resourceSpec.href);
         var cached = resourceCache[canon];
         if (cached.$$firer$$) {
             fluid.log("Handling request for " + canon + " from cache");
             var fetchClass = resourceSpec.fetchClass;
             if (fetchClass && pendingClass[fetchClass]) {
                 fluid.log("Clearing pendingClass entry for class " + fetchClass);
                 delete pendingClass[fetchClass][canon];
             }
             resourceCache[canon] = response;      
             cached.fire(response);
         }
    };
    
    /*
     * This function is unsupported: It is not really intended for use by implementors.
     */
    fluid.fetchResources.completeRequest = function(thisSpec, recurseCall) {
        thisSpec.queued = false;
        thisSpec.completeTime = new Date();
        fluid.log("Request to URL " + thisSpec.href + " completed - total elapsed time: " + 
            (thisSpec.completeTime.getTime() - thisSpec.initTime.getTime()) + "ms");
        thisSpec.recurseFirer.fire();
    };
  
    /*
     * This function is unsupported: It is not really intended for use by implementors.
     */
    fluid.fetchResources.makeResourceCallback = function(thisSpec) {
        return {
            success: function(response) {
                thisSpec.resourceText = response;
                thisSpec.resourceKey = thisSpec.href;
                if (thisSpec.forceCache) {
                    fluid.fetchResources.handleCachedRequest(thisSpec, response);
                }
                fluid.fetchResources.completeRequest(thisSpec);
            },
            error: function(response, textStatus, errorThrown) {
                thisSpec.fetchError = {
                    status: response.status,
                    textStatus: response.textStatus,
                    errorThrown: errorThrown
                };
                fluid.fetchResources.completeRequest(thisSpec);
            }
            
        };
    };
    
        
    /*
     * This function is unsupported: It is not really intended for use by implementors.
     */
    fluid.fetchResources.issueCachedRequest = function(resourceSpec, options) {
         var canon = canonUrl(resourceSpec.href);
         var cached = resourceCache[canon];
         if (!cached) {
             fluid.log("First request for cached resource with url " + canon);
             cached = fluid.event.getEventFirer(null, null, "cache notifier for resource URL " + canon);
             cached.$$firer$$ = true;
             resourceCache[canon] = cached;
             var fetchClass = resourceSpec.fetchClass;
             if (fetchClass) {
                 if (!pendingClass[fetchClass]) {
                     pendingClass[fetchClass] = {};
                 }
                 pendingClass[fetchClass][canon] = resourceSpec;
             }
             options.cache = false; // TODO: Getting weird "not modified" issues on Firefox
             $.ajax(options);
         }
         else {
             if (!cached.$$firer$$) {
                 options.success(cached);
             }
             else {
                 fluid.log("Request for cached resource which is in flight: url " + canon);
                 cached.addListener(function(response) {
                     options.success(response);
                 });
             }
         }
    };
    
    /*
     * This function is unsupported: It is not really intended for use by implementors.
     */
    // Compose callbacks in such a way that the 2nd, marked "external" will be applied
    // first if it exists, but in all cases, the first, marked internal, will be 
    // CALLED WITHOUT FAIL
    fluid.fetchResources.composeCallbacks = function(internal, external) {
        return external? function() {
            try {
                external.apply(null, arguments);
            }
            catch (e) {
                fluid.log("Exception applying external fetchResources callback: " + e);
            }
            internal.apply(null, arguments); // call the internal callback without fail
        } : internal;
    };
    
    /*
     * This function is unsupported: It is not really intended for use by implementors.
     */
    fluid.fetchResources.composePolicy = function(target, source, key) {
        return fluid.fetchResources.composeCallbacks(target, source);
    };
    
    fluid.defaults("fluid.fetchResources.issueRequest", {
        mergePolicy: {
            success: fluid.fetchResources.composePolicy,
            error: fluid.fetchResources.composePolicy,
            url: "reverse"
        }
    });
    
    /*
     * This function is unsupported: It is not really intended for use by implementors.
     */
    fluid.fetchResources.issueRequest = function(resourceSpec, key) {
        var thisCallback = fluid.fetchResources.makeResourceCallback(resourceSpec);
        var options = {  
             url:     resourceSpec.href,
             success: thisCallback.success, 
             error:   thisCallback.error,
             dataType: "text"};
        fluid.fetchResources.timeSuccessCallback(resourceSpec);
        fluid.merge(fluid.defaults("fluid.fetchResources.issueRequest").mergePolicy,
                      options, resourceSpec.options);
        resourceSpec.queued = true;
        resourceSpec.initTime = new Date();
        fluid.log("Request with key " + key + " queued for " + resourceSpec.href);

        if (resourceSpec.forceCache) {
            fluid.fetchResources.issueCachedRequest(resourceSpec, options);
        }
        else {
            $.ajax(options);
        }
    };
    
    fluid.fetchResources.fetchResourcesImpl = function(that) {
        var complete = true;
        var allSync = true;
        var resourceSpecs = that.resourceSpecs;
        for (var key in resourceSpecs) {
            var resourceSpec = resourceSpecs[key];
            if (!resourceSpec.options || resourceSpec.options.async) {
                allSync = false;
            }
            if (resourceSpec.href && !resourceSpec.completeTime) {
                 if (!resourceSpec.queued) {
                     fluid.fetchResources.issueRequest(resourceSpec, key);  
                 }
                 if (resourceSpec.queued) {
                     complete = false;
                 }
            }
            else if (resourceSpec.nodeId && !resourceSpec.resourceText) {
                var node = document.getElementById(resourceSpec.nodeId);
                // upgrade this to somehow detect whether node is "armoured" somehow
                // with comment or CDATA wrapping
                resourceSpec.resourceText = fluid.dom.getElementText(node);
                resourceSpec.resourceKey = resourceSpec.nodeId;
            }
        }
        if (complete && that.callback && !that.callbackCalled) {
            that.callbackCalled = true;
            if ($.browser.mozilla && !allSync) {
                // Defer this callback to avoid debugging problems on Firefox
                setTimeout(function() {
                    that.callback(resourceSpecs);
                    }, 1);
            }
            else {
                that.callback(resourceSpecs);
            }
        }
    };
    
    fluid.fetchResources.primeCacheFromResources = function(componentName) {
        var resources = fluid.defaults(componentName).resources;
        var that = {typeName: "fluid.fetchResources.primeCacheFromResources"};
        var expanded = (fluid.expandOptions ? fluid.expandOptions : fluid.identity)(fluid.copy(resources), that);
        fluid.fetchResources(expanded);
    };
    
    /** Utilities invoking requests for expansion **/
    fluid.registerNamespace("fluid.expander");
      
    /*
     * This function is unsupported: It is not really intended for use by implementors.
     */
    fluid.expander.makeDefaultFetchOptions = function (successdisposer, failid, options) {
        return $.extend(true, {dataType: "text"}, options, {
            success: function(response, environmentdisposer) {
                var json = JSON.parse(response);
                environmentdisposer(successdisposer(json));
            },
            error: function(response, textStatus) {
                fluid.log("Error fetching " + failid + ": " + textStatus);
            }
        });
    };
  
    /*
     * This function is unsupported: It is not really intended for use by implementors.
     */
    fluid.expander.makeFetchExpander = function (options) {
        return { expander: {
            type: "fluid.expander.deferredFetcher",
            href: options.url,
            options: fluid.expander.makeDefaultFetchOptions(options.disposer, options.url, options.options),
            resourceSpecCollector: "{resourceSpecCollector}",
            fetchKey: options.fetchKey
        }};
    };
    
    fluid.expander.deferredFetcher = function(target, source, recurse, expandOptions) {
        var expander = source.expander;
        var spec = fluid.copy(expander);
        // fetch the "global" collector specified in the external environment to receive
        // this resourceSpec
        var collector = fluid.resolveEnvironment(expander.resourceSpecCollector, expandOptions);
        delete spec.type;
        delete spec.resourceSpecCollector;
        delete spec.fetchKey;
        var environmentdisposer = function(disposed) {
            $.extend(target, disposed);
        };
        // replace the callback which is there (taking 2 arguments) with one which
        // directly responds to the request, passing in the result and OUR "disposer" - 
        // which once the user has processed the response (say, parsing JSON and repackaging)
        // finally deposits it in the place of the expander in the tree to which this reference
        // has been stored at the point this expander was evaluated.
        spec.options.success = function(response) {
             expander.options.success(response, environmentdisposer);
        };
        var key = expander.fetchKey || fluid.allocateGuid();
        collector[key] = spec;
        return target;
    };
    
    
})(jQuery, fluid_1_5);
// =========================================================================
//
// tinyxmlsax.js - an XML SAX parser in JavaScript compressed for downloading
//
// version 3.1
//
// =========================================================================
//
// Copyright (C) 2000 - 2002, 2003 Michael Houghton (mike@idle.org), Raymond Irving and David Joham (djoham@yahoo.com)
//
// This library is free software; you can redistribute it and/or
// modify it under the terms of the GNU Lesser General Public
// License as published by the Free Software Foundation; either
// version 2.1 of the License, or (at your option) any later version.

// This library is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
// Lesser General Public License for more details.

// You should have received a copy of the GNU Lesser General Public
// License along with this library; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//
// Visit the XML for <SCRIPT> home page at http://xmljs.sourceforge.net
//

/*
The zlib/libpng License

Copyright (c) 2000 - 2002, 2003 Michael Houghton (mike@idle.org), Raymond Irving and David Joham (djoham@yahoo.com)

This software is provided 'as-is', without any express or implied
warranty. In no event will the authors be held liable for any damages
arising from the use of this software.

Permission is granted to anyone to use this software for any purpose,
including commercial applications, and to alter it and redistribute it
freely, subject to the following restrictions:

    1. The origin of this software must not be misrepresented; you must not
    claim that you wrote the original software. If you use this software
    in a product, an acknowledgment in the product documentation would be
    appreciated but is not required.

    2. Altered source versions must be plainly marked as such, and must not be
    misrepresented as being the original software.

    3. This notice may not be removed or altered from any source
    distribution.
 */

// Declare dependencies
/*global fluid_1_5:true, jQuery*/

// JSLint options 
/*jslint white: true, funcinvoke: true, undef: true, newcap: true, nomen: true, regexp: true, bitwise: true, browser: true, forin: true, maxerr: 100, indent: 4 */

var fluid_1_5 = fluid_1_5 || {};

(function ($, fluid) {
    
    fluid.XMLP = function(strXML) {
        return fluid.XMLP.XMLPImpl(strXML);
    };

        
    // List of closed HTML tags, taken from JQuery 1.2.3
    fluid.XMLP.closedTags = {
        abbr: true, br: true, col: true, img: true, input: true,
        link: true, meta: true, param: true, hr: true, area: true, embed:true
        };

    fluid.XMLP._NONE = 0;
    fluid.XMLP._ELM_B = 1;
    fluid.XMLP._ELM_E = 2;
    fluid.XMLP._ELM_EMP = 3; 
    fluid.XMLP._ATT = 4;
    fluid.XMLP._TEXT = 5;
    fluid.XMLP._ENTITY = 6; 
    fluid.XMLP._PI = 7;
    fluid.XMLP._CDATA = 8;
    fluid.XMLP._COMMENT = 9; 
    fluid.XMLP._DTD = 10;
    fluid.XMLP._ERROR = 11;
     
    fluid.XMLP._CONT_XML = 0; 
    fluid.XMLP._CONT_ALT = 1; 
    fluid.XMLP._ATT_NAME = 0; 
    fluid.XMLP._ATT_VAL = 1;
    
    fluid.XMLP._STATE_PROLOG = 1;
    fluid.XMLP._STATE_DOCUMENT = 2; 
    fluid.XMLP._STATE_MISC = 3;
    
    fluid.XMLP._errs = [];
    fluid.XMLP._errs[fluid.XMLP.ERR_CLOSE_PI = 0 ] = "PI: missing closing sequence"; 
    fluid.XMLP._errs[fluid.XMLP.ERR_CLOSE_DTD = 1 ] = "DTD: missing closing sequence"; 
    fluid.XMLP._errs[fluid.XMLP.ERR_CLOSE_COMMENT = 2 ] = "Comment: missing closing sequence"; 
    fluid.XMLP._errs[fluid.XMLP.ERR_CLOSE_CDATA = 3 ] = "CDATA: missing closing sequence"; 
    fluid.XMLP._errs[fluid.XMLP.ERR_CLOSE_ELM = 4 ] = "Element: missing closing sequence"; 
    fluid.XMLP._errs[fluid.XMLP.ERR_CLOSE_ENTITY = 5 ] = "Entity: missing closing sequence"; 
    fluid.XMLP._errs[fluid.XMLP.ERR_PI_TARGET = 6 ] = "PI: target is required"; 
    fluid.XMLP._errs[fluid.XMLP.ERR_ELM_EMPTY = 7 ] = "Element: cannot be both empty and closing"; 
    fluid.XMLP._errs[fluid.XMLP.ERR_ELM_NAME = 8 ] = "Element: name must immediatly follow \"<\""; 
    fluid.XMLP._errs[fluid.XMLP.ERR_ELM_LT_NAME = 9 ] = "Element: \"<\" not allowed in element names"; 
    fluid.XMLP._errs[fluid.XMLP.ERR_ATT_VALUES = 10] = "Attribute: values are required and must be in quotes"; 
    fluid.XMLP._errs[fluid.XMLP.ERR_ATT_LT_NAME = 11] = "Element: \"<\" not allowed in attribute names"; 
    fluid.XMLP._errs[fluid.XMLP.ERR_ATT_LT_VALUE = 12] = "Attribute: \"<\" not allowed in attribute values"; 
    fluid.XMLP._errs[fluid.XMLP.ERR_ATT_DUP = 13] = "Attribute: duplicate attributes not allowed"; 
    fluid.XMLP._errs[fluid.XMLP.ERR_ENTITY_UNKNOWN = 14] = "Entity: unknown entity"; 
    fluid.XMLP._errs[fluid.XMLP.ERR_INFINITELOOP = 15] = "Infinite loop"; 
    fluid.XMLP._errs[fluid.XMLP.ERR_DOC_STRUCTURE = 16] = "Document: only comments, processing instructions, or whitespace allowed outside of document element"; 
    fluid.XMLP._errs[fluid.XMLP.ERR_ELM_NESTING = 17] = "Element: must be nested correctly"; 
                

    fluid.XMLP._checkStructure = function(that, iEvent) {
        var stack = that.m_stack; 
        if (fluid.XMLP._STATE_PROLOG == that.m_iState) {
            // disabled original check for text node in prologue
            that.m_iState = fluid.XMLP._STATE_DOCUMENT;
            }
    
        if (fluid.XMLP._STATE_DOCUMENT === that.m_iState) {
            if ((fluid.XMLP._ELM_B == iEvent) || (fluid.XMLP._ELM_EMP == iEvent)) { 
                that.m_stack[stack.length] = that.getName();
                }
            if ((fluid.XMLP._ELM_E == iEvent) || (fluid.XMLP._ELM_EMP == iEvent)) {
                if (stack.length === 0) {
                    //return this._setErr(XMLP.ERR_DOC_STRUCTURE);
                    return fluid.XMLP._NONE;
                    }
                var strTop = stack[stack.length - 1];
                that.m_stack.length--;
                if (strTop === null || strTop !== that.getName()) { 
                    return that._setErr(that, fluid.XMLP.ERR_ELM_NESTING);
                    }
                }
    
            // disabled original check for text node in epilogue - "MISC" state is disused
        }
        return iEvent;
    };
    
            
    fluid.XMLP._parseCDATA = function(that, iB) { 
        var iE = that.m_xml.indexOf("]]>", iB); 
        if (iE == -1) { return fluid.XMLP._setErr(that, fluid.XMLP.ERR_CLOSE_CDATA);}
        fluid.XMLP._setContent(that, fluid.XMLP._CONT_XML, iB, iE); 
        that.m_iP = iE + 3; 
        return fluid.XMLP._CDATA;
        };
        
    
    fluid.XMLP._parseComment = function(that, iB) { 
        var iE = that.m_xml.indexOf("-" + "->", iB); 
        if (iE == -1) { 
            return fluid.XMLP._setErr(that, fluid.XMLP.ERR_CLOSE_COMMENT);
            }
        fluid.XMLP._setContent(that, fluid.XMLP._CONT_XML, iB - 4, iE + 3); 
        that.m_iP = iE + 3; 
        return fluid.XMLP._COMMENT;
        };    
    
    fluid.XMLP._parseDTD = function(that, iB) { 
        var iE, strClose, iInt, iLast; 
        iE = that.m_xml.indexOf(">", iB); 
        if (iE == -1) { 
            return fluid.XMLP._setErr(that, fluid.XMLP.ERR_CLOSE_DTD);
            }
        iInt = that.m_xml.indexOf("[", iB); 
        strClose = ((iInt != -1) && (iInt < iE)) ? "]>" : ">"; 
        while (true) { 
            if (iE == iLast) { 
                return fluid.XMLP._setErr(that, fluid.XMLP.ERR_INFINITELOOP);
                }
            iLast = iE; 
            iE = that.m_xml.indexOf(strClose, iB); 
            if(iE == -1) { 
                return fluid.XMLP._setErr(that, fluid.XMLP.ERR_CLOSE_DTD);
                }
            if (that.m_xml.substring(iE - 1, iE + 2) != "]]>") { break;}
            }
        that.m_iP = iE + strClose.length; 
        return fluid.XMLP._DTD;
        };
        
    fluid.XMLP._parsePI = function(that, iB) { 
        var iE, iTB, iTE, iCB, iCE; 
        iE = that.m_xml.indexOf("?>", iB); 
        if (iE == -1) { return fluid.XMLP._setErr(that, fluid.XMLP.ERR_CLOSE_PI);}
        iTB = fluid.SAXStrings.indexOfNonWhitespace(that.m_xml, iB, iE); 
        if (iTB == -1) { return fluid.XMLP._setErr(that, fluid.XMLP.ERR_PI_TARGET);}
        iTE = fluid.SAXStrings.indexOfWhitespace(that.m_xml, iTB, iE); 
        if (iTE == -1) { iTE = iE;}
        iCB = fluid.SAXStrings.indexOfNonWhitespace(that.m_xml, iTE, iE); 
        if (iCB == -1) { iCB = iE;}
        iCE = fluid.SAXStrings.lastIndexOfNonWhitespace(that.m_xml, iCB, iE); 
        if (iCE == -1) { iCE = iE - 1;}
        that.m_name = that.m_xml.substring(iTB, iTE); 
        fluid.XMLP._setContent(that, fluid.XMLP._CONT_XML, iCB, iCE + 1); 
        that.m_iP = iE + 2; 
        return fluid.XMLP._PI;
        };
        
    fluid.XMLP._parseText = function(that, iB) { 
        var iE = that.m_xml.indexOf("<", iB);
        if (iE == -1) { iE = that.m_xml.length;}
        fluid.XMLP._setContent(that, fluid.XMLP._CONT_XML, iB, iE); 
        that.m_iP = iE; 
        return fluid.XMLP._TEXT;
        };
        
    fluid.XMLP._setContent = function(that, iSrc) { 
        var args = arguments; 
        if (fluid.XMLP._CONT_XML == iSrc) { 
            that.m_cAlt = null; 
            that.m_cB = args[2]; 
            that.m_cE = args[3];
            } 
        else { 
            that.m_cAlt = args[2]; 
            that.m_cB = 0; 
            that.m_cE = args[2].length;
            }
            
        that.m_cSrc = iSrc;
        };
        
    fluid.XMLP._setErr = function(that, iErr) { 
        var strErr = fluid.XMLP._errs[iErr]; 
        that.m_cAlt = strErr; 
        that.m_cB = 0; 
        that.m_cE = strErr.length; 
        that.m_cSrc = fluid.XMLP._CONT_ALT; 
        return fluid.XMLP._ERROR;
        };
            
    
    fluid.XMLP._parseElement = function(that, iB) {
        var iE, iDE, iRet; 
        var iType, strN, iLast; 
        iDE = iE = that.m_xml.indexOf(">", iB); 
        if (iE == -1) { 
            return that._setErr(that, fluid.XMLP.ERR_CLOSE_ELM);
            }
        if (that.m_xml.charAt(iB) == "/") { 
            iType = fluid.XMLP._ELM_E; 
            iB++;
            } 
        else { 
            iType = fluid.XMLP._ELM_B;
            }
        if (that.m_xml.charAt(iE - 1) == "/") { 
            if (iType == fluid.XMLP._ELM_E) { 
                return fluid.XMLP._setErr(that, fluid.XMLP.ERR_ELM_EMPTY);
                }
            iType = fluid.XMLP._ELM_EMP; iDE--;
            }
    
        that.nameRegex.lastIndex = iB;
        var nameMatch = that.nameRegex.exec(that.m_xml);
        if (!nameMatch) {
            return fluid.XMLP._setErr(that, fluid.XMLP.ERR_ELM_NAME);
            }
        strN = nameMatch[1].toLowerCase();
        // This branch is specially necessary for broken markup in IE. If we see an li
        // tag apparently directly nested in another, first emit a synthetic close tag
        // for the earlier one without advancing the pointer, and set a flag to ensure
        // doing this just once.
        if ("li" === strN && iType !== fluid.XMLP._ELM_E && that.m_stack.length > 0 && 
            that.m_stack[that.m_stack.length - 1] === "li" && !that.m_emitSynthetic) {
            that.m_name = "li";
            that.m_emitSynthetic = true;
            return fluid.XMLP._ELM_E;
        }
        // We have acquired the tag name, now set about parsing any attribute list
        that.m_attributes = {};
        that.m_cAlt = ""; 
    
        if (that.nameRegex.lastIndex < iDE) {
            that.m_iP = that.nameRegex.lastIndex;
            while (that.m_iP < iDE) {
                that.attrStartRegex.lastIndex = that.m_iP;
                var attrMatch = that.attrStartRegex.exec(that.m_xml);
                if (!attrMatch) {
                    return fluid.XMLP._setErr(that, fluid.XMLP.ERR_ATT_VALUES);
                    }
                var attrname = attrMatch[1].toLowerCase();
                var attrval;
                if (that.m_xml.charCodeAt(that.attrStartRegex.lastIndex) === 61) { // = 
                    var valRegex = that.m_xml.charCodeAt(that.attrStartRegex.lastIndex + 1) === 34? that.attrValRegex : that.attrValIERegex; // "
                    valRegex.lastIndex = that.attrStartRegex.lastIndex + 1;
                    attrMatch = valRegex.exec(that.m_xml);
                    if (!attrMatch) {
                        return fluid.XMLP._setErr(that, fluid.XMLP.ERR_ATT_VALUES);
                        }
                    attrval = attrMatch[1];
                    }
                else { // accommodate insanity on unvalued IE attributes
                    attrval = attrname;
                    valRegex = that.attrStartRegex;
                    }
                if (!that.m_attributes[attrname]) {
                    that.m_attributes[attrname] = attrval;
                    }
                else { 
                    return fluid.XMLP._setErr(that, fluid.XMLP.ERR_ATT_DUP);
                }
                that.m_iP = valRegex.lastIndex;
                    
                }
            }
        if (strN.indexOf("<") != -1) { 
            return fluid.XMLP._setErr(that, fluid.XMLP.ERR_ELM_LT_NAME);
            }
    
        that.m_name = strN; 
        that.m_iP = iE + 1;
        // Check for corrupted "closed tags" from innerHTML
        if (fluid.XMLP.closedTags[strN]) {
            that.closeRegex.lastIndex = iE + 1;
            var closeMatch = that.closeRegex.exec;
            if (closeMatch) {
                var matchclose = that.m_xml.indexOf(strN, closeMatch.lastIndex);
                if (matchclose === closeMatch.lastIndex) {
                    return iType; // bail out, a valid close tag is separated only by whitespace
                }
                else {
                    return fluid.XMLP._ELM_EMP;
                }
            }
        }
        that.m_emitSynthetic = false;
        return iType;
    };
    
    fluid.XMLP._parse = function(that) {
        var iP = that.m_iP;
        var xml = that.m_xml; 
        if (iP === xml.length) { return fluid.XMLP._NONE;}
        var c = xml.charAt(iP);
        if (c === '<') {
            var c2 = xml.charAt(iP + 1);
            if (c2 === '?') {
                return fluid.XMLP._parsePI(that, iP + 2);
                }
            else if (c2 === '!') {
                if (iP === xml.indexOf("<!DOCTYPE", iP)) { 
                    return fluid.XMLP._parseDTD(that, iP + 9);
                    }
                else if (iP === xml.indexOf("<!--", iP)) { 
                    return fluid.XMLP._parseComment(that, iP + 4);
                    }
                else if (iP === xml.indexOf("<![CDATA[", iP)) { 
                    return fluid.XMLP._parseCDATA(that, iP + 9);
                    }
                }
            else {
                return fluid.XMLP._parseElement(that, iP + 1);
                }
            }
        else {
            return fluid.XMLP._parseText(that, iP);
            }
        };
        
    
    fluid.XMLP.XMLPImpl = function(strXML) { 
        var that = {};    
        that.m_xml = strXML; 
        that.m_iP = 0;
        that.m_iState = fluid.XMLP._STATE_PROLOG; 
        that.m_stack = [];
        that.m_attributes = {};
        that.m_emitSynthetic = false; // state used for emitting synthetic tags used to correct broken markup (IE)
        
        that.getColumnNumber = function() { 
            return fluid.SAXStrings.getColumnNumber(that.m_xml, that.m_iP);
        };
        
        that.getContent = function() { 
            return (that.m_cSrc == fluid.XMLP._CONT_XML) ? that.m_xml : that.m_cAlt;
        };
        
        that.getContentBegin = function() { return that.m_cB;};
        that.getContentEnd = function() { return that.m_cE;};
    
        that.getLineNumber = function() { 
            return fluid.SAXStrings.getLineNumber(that.m_xml, that.m_iP);
        };
        
        that.getName = function() { 
            return that.m_name;
        };
        
        that.next = function() { 
            return fluid.XMLP._checkStructure(that, fluid.XMLP._parse(that));
        };
    
        that.nameRegex = /([^\s\/>]+)/g;
        that.attrStartRegex = /\s*([\w:_][\w:_\-\.]*)/gm;
        that.attrValRegex = /\"([^\"]*)\"\s*/gm; // "normal" XHTML attribute values
        that.attrValIERegex = /([^\>\s]+)\s*/gm; // "stupid" unquoted IE attribute values (sometimes)
        that.closeRegex = /\s*<\//g;

        return that;
    };
    
    
    fluid.SAXStrings = {};
    
    fluid.SAXStrings.WHITESPACE = " \t\n\r"; 
    fluid.SAXStrings.QUOTES = "\"'"; 
    fluid.SAXStrings.getColumnNumber = function (strD, iP) { 
        if (!strD) { return -1;}
        iP = iP || strD.length; 
        var arrD = strD.substring(0, iP).split("\n"); 
        arrD.length--; 
        var iLinePos = arrD.join("\n").length; 
        return iP - iLinePos;
        };
        
    fluid.SAXStrings.getLineNumber = function (strD, iP) { 
        if (!strD) { return -1;}
        iP = iP || strD.length; 
        return strD.substring(0, iP).split("\n").length;
        };
        
    fluid.SAXStrings.indexOfNonWhitespace = function (strD, iB, iE) {
        if (!strD) return -1;
        iB = iB || 0; 
        iE = iE || strD.length; 
        
        for (var i = iB; i < iE; ++ i) { 
            var c = strD.charAt(i);
            if (c !== ' ' && c !== '\t' && c !== '\n' && c !== '\r') return i;
            }
        return -1;
        };
        
        
    fluid.SAXStrings.indexOfWhitespace = function (strD, iB, iE) { 
        if (!strD) { return -1;}
            iB = iB || 0; 
            iE = iE || strD.length; 
            for (var i = iB; i < iE; i++) { 
                if (fluid.SAXStrings.WHITESPACE.indexOf(strD.charAt(i)) != -1) { return i;}
            }
        return -1;
        };
        
        
    fluid.SAXStrings.lastIndexOfNonWhitespace = function (strD, iB, iE) { 
            if (!strD) { return -1;}
            iB = iB || 0; iE = iE || strD.length; 
            for (var i = iE - 1; i >= iB; i--) { 
            if (fluid.SAXStrings.WHITESPACE.indexOf(strD.charAt(i)) == -1) { 
                return i;
                }
            }
        return -1;
        };
        
    fluid.SAXStrings.replace = function(strD, iB, iE, strF, strR) { 
        if (!strD) { return "";}
        iB = iB || 0; 
        iE = iE || strD.length; 
        return strD.substring(iB, iE).split(strF).join(strR);
        };
            
})(jQuery, fluid_1_5);
        /*
Copyright 2008-2010 University of Cambridge
Copyright 2008-2009 University of Toronto
Copyright 2010-2011 Lucendo Development Ltd.

Licensed under the Educational Community License (ECL), Version 2.0 or the New
BSD license. You may not use this file except in compliance with one these
Licenses.

You may obtain a copy of the ECL 2.0 License and BSD License at
https://github.com/fluid-project/infusion/raw/master/Infusion-LICENSE.txt
*/

// Declare dependencies
/*global fluid_1_5:true, jQuery*/

// JSLint options 
/*jslint white: true, funcinvoke: true, continue: true, elsecatch: true, operator: true, jslintok:true, undef: true, newcap: true, regexp: true, bitwise: true, browser: true, forin: true, maxerr: 100, indent: 4 */

fluid_1_5 = fluid_1_5 || {};

(function ($, fluid) {
      
    fluid.parseTemplate = function (template, baseURL, scanStart, cutpoints_in, opts) {
        opts = opts || {};
      
        if (!template) {
            fluid.fail("empty template supplied to fluid.parseTemplate");
        }
      
        var t;
        var parser;
        var tagstack;
        var lumpindex = 0;
        var nestingdepth = 0;
        var justended = false;
        
        var defstart = -1;
        var defend = -1;   
        
        var debugMode = false;
        
        var cutpoints = []; // list of selector, tree, id
        var simpleClassCutpoints = {};
        
        var cutstatus = [];
        
        var XMLLump = function (lumpindex, nestingdepth) {
            return {
                //rsfID: "",
                //text: "",
                //downmap: {},
                //attributemap: {},
                //finallump: {},
                nestingdepth: nestingdepth,
                lumpindex: lumpindex,
                parent: t
            };
        };
        
        function isSimpleClassCutpoint(tree) {
            return tree.length === 1 && tree[0].predList.length === 1 && tree[0].predList[0].clazz;
        }
        
        function init(baseURLin, debugModeIn, cutpointsIn) {
            t.rootlump = XMLLump(0, -1); // jslint:ok - capital letter
            tagstack = [t.rootlump];
            lumpindex = 0;
            nestingdepth = 0;
            justended = false;
            defstart = -1;
            defend = -1;
            baseURL = baseURLin;
            debugMode = debugModeIn;
            if (cutpointsIn) {
                for (var i = 0; i < cutpointsIn.length; ++i) {
                    var tree = fluid.parseSelector(cutpointsIn[i].selector);
                    var clazz = isSimpleClassCutpoint(tree);
                    if (clazz) {
                        simpleClassCutpoints[clazz] = cutpointsIn[i].id;
                    }
                    else {
                        cutstatus.push([]);
                        cutpoints.push($.extend({}, cutpointsIn[i], {tree: tree}));
                    }
                }
            }
        }
        
        function findTopContainer() {
            for (var i = tagstack.length - 1; i >= 0; --i) {
                var lump = tagstack[i];
                if (lump.rsfID !== undefined) {
                    return lump;
                }
            }
            return t.rootlump;
        }
        
        function newLump() {
            var togo = XMLLump(lumpindex, nestingdepth); // jslint:ok - capital letter
            if (debugMode) {
                togo.line = parser.getLineNumber();
                togo.column = parser.getColumnNumber();
            }
            //togo.parent = t;
            t.lumps[lumpindex] = togo;
            ++lumpindex;
            return togo;
        }
        
        function addLump(mmap, ID, lump) {
            var list = mmap[ID];
            if (!list) {
                list = [];
                mmap[ID] = list;
            }
            list[list.length] = lump;
        }
          
        function checkContribute(ID, lump) {
            if (ID.indexOf("scr=contribute-") !== -1) {
                var scr = ID.substring("scr=contribute-".length);
                addLump(t.collectmap, scr, lump);
            }
        }
        
        function debugLump(lump) {
          // TODO expand this to agree with the Firebug "self-selector" idiom
            return "<" + lump.tagname + ">";
        }
        
        function hasCssClass(clazz, totest) {
            if (!totest) {
                return false;
            }
            // algorithm from JQuery
            return (" " + totest + " ").indexOf(" " + clazz + " ") !== -1;
        }
        
        function matchNode(term, headlump, headclazz) {
            if (term.predList) {
                for (var i = 0; i < term.predList.length; ++i) {
                    var pred = term.predList[i];
                    if (pred.id && headlump.attributemap.id !== pred.id) {return false;}
                    if (pred.clazz && !hasCssClass(pred.clazz, headclazz)) {return false;}
                    if (pred.tag && headlump.tagname !== pred.tag) {return false;}
                }
                return true;
            }
        }
        
        function tagStartCut(headlump) {
            var togo;
            var headclazz = headlump.attributemap["class"];
            if (headclazz) {
                var split = headclazz.split(" ");
                for (var i = 0; i < split.length; ++i) {
                    var simpleCut = simpleClassCutpoints[$.trim(split[i])];
                    if (simpleCut) {
                        return simpleCut;
                    }
                }
            }
            for (var i = 0; i < cutpoints.length; ++i) { // jslint:ok - scoping
                var cut = cutpoints[i];
                var cutstat = cutstatus[i];
                var nextterm = cutstat.length; // the next term for this node
                if (nextterm < cut.tree.length) {
                    var term = cut.tree[nextterm];
                    if (nextterm > 0) {
                        if (cut.tree[nextterm - 1].child && 
                                cutstat[nextterm - 1] !== headlump.nestingdepth - 1) {
                            continue; // it is a failure to match if not at correct nesting depth 
                        }
                    }
                    var isMatch = matchNode(term, headlump, headclazz);
                    if (isMatch) {
                        cutstat[cutstat.length] = headlump.nestingdepth;
                        if (cutstat.length === cut.tree.length) {
                            if (togo !== undefined) {
                                fluid.fail("Cutpoint specification error - node " +
                                    debugLump(headlump) +
                                    " has already matched with rsf:id of " + togo);
                            }
                            if (cut.id === undefined || cut.id === null) {
                                fluid.fail("Error in cutpoints list - entry at position " + i + " does not have an id set");
                            }
                            togo = cut.id;
                        }
                    }
                }
            }
            return togo;
        }
          
        function tagEndCut() {
            if (cutpoints) {
                for (var i = 0; i < cutpoints.length; ++i) {
                    var cutstat = cutstatus[i];
                    if (cutstat.length > 0 && cutstat[cutstat.length - 1] === nestingdepth) {
                        cutstat.length--;
                    }
                }
            }
        }
        
        function processTagEnd() {
            tagEndCut();
            var endlump = newLump();
            --nestingdepth;
            endlump.text = "</" + parser.getName() + ">";
            var oldtop = tagstack[tagstack.length - 1];
            oldtop.close_tag = t.lumps[lumpindex - 1];
            tagstack.length--;
            justended = true;
        }
        
        function processTagStart(isempty, text) {
            ++nestingdepth;
            if (justended) {
                justended = false;
                var backlump = newLump();
                backlump.nestingdepth--;
            }
            if (t.firstdocumentindex === -1) {
                t.firstdocumentindex = lumpindex;
            }
            var headlump = newLump();
            var stacktop = tagstack[tagstack.length - 1];
            headlump.uplump = stacktop;
            var tagname = parser.getName();
            headlump.tagname = tagname;
            // NB - attribute names and values are now NOT DECODED!!
            var attrs = headlump.attributemap = parser.m_attributes;
            var ID = attrs[fluid.ID_ATTRIBUTE];
            if (ID === undefined) {
                ID = tagStartCut(headlump);
            }
            for (var attrname in attrs) {
                if (ID === undefined) {
                    if (/href|src|codebase|action/.test(attrname)) {
                        ID = "scr=rewrite-url";
                    }
                    // port of TPI effect of IDRelationRewriter
                    else if (ID === undefined && /for|headers/.test(attrname)) {
                        ID = "scr=null";
                    }
                }
            }
        
            if (ID) {
                // TODO: ensure this logic is correct on RSF Server
                if (ID.charCodeAt(0) === 126) { // "~"
                    ID = ID.substring(1);
                    headlump.elide = true;
                }
                checkContribute(ID, headlump);
                headlump.rsfID = ID;
                var downreg = findTopContainer();
                if (!downreg.downmap) {
                    downreg.downmap = {};
                }
                while (downreg) { // TODO: unusual fix for locating branches in parent contexts (applies to repetitive leaves)
                    if (downreg.downmap) {
                        addLump(downreg.downmap, ID, headlump);
                    }
                    downreg = downreg.uplump;
                }
                addLump(t.globalmap, ID, headlump);
                var colpos = ID.indexOf(":");
                if (colpos !== -1) {
                    var prefix = ID.substring(0, colpos);
                    if (!stacktop.finallump) {
                        stacktop.finallump = {};
                    }
                    stacktop.finallump[prefix] = headlump;
                }
            }
            
            // TODO: accelerate this by grabbing original template text (requires parser
            // adjustment) as well as dealing with empty tags
            headlump.text = "<" + tagname + fluid.dumpAttributes(attrs) + (isempty && !ID? "/>" : ">");
            tagstack[tagstack.length] = headlump;
            if (isempty) {
                if (ID) {
                    processTagEnd();
                }
                else {
                    --nestingdepth;
                    tagstack.length--;
                }
            }
        }
        

        
        function processDefaultTag() {
            if (defstart !== -1) {
                if (t.firstdocumentindex === -1) {
                    t.firstdocumentindex = lumpindex;
                }
                var text = parser.getContent().substr(defstart, defend - defstart);
                justended = false;
                var newlump = newLump();
                newlump.text = text; 
                defstart = -1;
            }
        }
       
       /** ACTUAL BODY of fluid.parseTemplate begins here **/
          
        t = fluid.XMLViewTemplate();
        
        init(baseURL, opts.debugMode, cutpoints_in);
    
        var idpos = template.indexOf(fluid.ID_ATTRIBUTE);
        if (scanStart) {
            var brackpos = template.indexOf('>', idpos);
            parser = fluid.XMLP(template.substring(brackpos + 1));
        }
        else {
            parser = fluid.XMLP(template); 
        }
    
parseloop: while (true) {
            var iEvent = parser.next();
            switch (iEvent) {
            case fluid.XMLP._ELM_B:
                processDefaultTag();
                //var text = parser.getContent().substr(parser.getContentBegin(), parser.getContentEnd() - parser.getContentBegin());
                processTagStart(false, "");
                break;
            case fluid.XMLP._ELM_E:
                processDefaultTag();
                processTagEnd();
                break;
            case fluid.XMLP._ELM_EMP:
                processDefaultTag();
                //var text = parser.getContent().substr(parser.getContentBegin(), parser.getContentEnd() - parser.getContentBegin());    
                processTagStart(true, "");
                break;
            case fluid.XMLP._PI:
            case fluid.XMLP._DTD:
                defstart = -1;
                continue; // not interested in reproducing these
            case fluid.XMLP._TEXT:
            case fluid.XMLP._ENTITY:
            case fluid.XMLP._CDATA:
            case fluid.XMLP._COMMENT:
                if (defstart === -1) {
                    defstart = parser.m_cB;
                }
                defend = parser.m_cE;
                break;
            case fluid.XMLP._ERROR:
                fluid.setLogging(true);
                var message = "Error parsing template: " + parser.m_cAlt + " at line " + parser.getLineNumber(); 
                fluid.log(message);
                fluid.log("Just read: " + parser.m_xml.substring(parser.m_iP - 30, parser.m_iP));
                fluid.log("Still to read: " + parser.m_xml.substring(parser.m_iP, parser.m_iP + 30));
                fluid.fail(message);
                break parseloop;
            case fluid.XMLP._NONE:
                break parseloop;
            }
        }
        processDefaultTag();
        var excess = tagstack.length - 1; 
        if (excess) {
            fluid.fail("Error parsing template - unclosed tag(s) of depth " + (excess) + 
                ": " + fluid.transform(tagstack.splice(1, excess), function (lump) {return debugLump(lump);}).join(", "));
        }
        return t;
    };
    
    fluid.debugLump = function (lump) {
        var togo = lump.text;
        togo += " at ";
        togo += "lump line " + lump.line + " column " + lump.column + " index " + lump.lumpindex;
        togo += lump.parent.href === null? "" : " in file " + lump.parent.href;
        return togo;
    };
    
    // Public definitions begin here
    
    fluid.ID_ATTRIBUTE = "rsf:id";
    
    fluid.getPrefix = function (id) {
        var colpos = id.indexOf(':');
        return colpos === -1? id : id.substring(0, colpos);
    };
    
    fluid.SplitID = function (id) {
        var that = {};
        var colpos = id.indexOf(':');
        if (colpos === -1) {
            that.prefix = id;
        }
        else {
            that.prefix = id.substring(0, colpos);
            that.suffix = id.substring(colpos + 1);
        }
        return that;
    };
    
    fluid.XMLViewTemplate = function () {
        return {
            globalmap: {},
            collectmap: {},
            lumps: [],
            firstdocumentindex: -1
        };
    };
    
      // TODO: find faster encoder
    fluid.XMLEncode = function (text) {
        return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/\"/g, "&quot;"); 
    };
    
    fluid.dumpAttributes = function (attrcopy) {
        var togo = "";
        for (var attrname in attrcopy) {
            var attrvalue = attrcopy[attrname];
            if (attrvalue !== null && attrvalue !== undefined) {
                togo += " " + attrname + "=\"" + attrvalue + "\"";
            }
        }
        return togo;
    };
    
    fluid.aggregateMMap = function (target, source) {
        for (var key in source) {
            var targhas = target[key];
            if (!targhas) {
                target[key] = [];
            }
            target[key] = target[key].concat(source[key]);
        }
    };
  
    
    
    /** Returns a "template structure", with globalmap in the root, and a list
     * of entries {href, template, cutpoints} for each parsed template.
     */
    fluid.parseTemplates = function (resourceSpec, templateList, opts) {
        var togo = [];
        opts = opts || {};
        togo.globalmap = {};
        for (var i = 0; i < templateList.length; ++i) {
            var resource = resourceSpec[templateList[i]];
            var lastslash = resource.href.lastIndexOf("/");
            var baseURL = lastslash === -1? "" : resource.href.substring(0, lastslash + 1);
              
            var template = fluid.parseTemplate(resource.resourceText, baseURL, 
                opts.scanStart && i === 0, resource.cutpoints, opts);
            if (i === 0) {
                fluid.aggregateMMap(togo.globalmap, template.globalmap);
            }
            template.href = resource.href;
            template.baseURL = baseURL;
            template.resourceKey = resource.resourceKey;
      
            togo[i] = template;
            fluid.aggregateMMap(togo.globalmap, template.rootlump.downmap);
        }
        return togo;
    };
  
    // ******* SELECTOR ENGINE *********  
      
    // selector regexps copied from JQuery
    var chars = "(?:[\\w\u0128-\uFFFF*_-]|\\\\.)";
//    var quickChild = new RegExp("^>\\s*(" + chars + "+)");
//    var quickID = new RegExp("^(" + chars + "+)(#)(" + chars + "+)");
//    var selSeg = new RegExp("^\\s*([#.]?)(" + chars + "*)");
  
    var quickClass = new RegExp("([#.]?)(" + chars + "+)", "g");
    var childSeg = new RegExp("\\s*(>)?\\s*", "g");
//    var whiteSpace = new RegExp("^\\w*$");
  
    fluid.parseSelector = function (selstring) {
        var togo = [];
        selstring = $.trim(selstring);
        //ws-(ss*)[ws/>]
        quickClass.lastIndex = 0;
        var lastIndex = 0;
        while (true) {
            var atNode = []; // a list of predicates at a particular node
            while (true) {
                var segMatch = quickClass.exec(selstring);
                if (!segMatch || segMatch.index !== lastIndex) {
                    break;
                }
                var thisNode = {};
                var text = segMatch[2];
                if (segMatch[1] === "") {
                    thisNode.tag = text;
                }
                else if (segMatch[1] === "#") {
                    thisNode.id = text;
                }
                else if (segMatch[1] === ".") {
                    thisNode.clazz = text;
                }
                atNode[atNode.length] = thisNode;
                lastIndex = quickClass.lastIndex;
            }
            childSeg.lastIndex = lastIndex;
            var fullAtNode = {predList: atNode};
            var childMatch = childSeg.exec(selstring);
            if (!childMatch || childMatch.index !== lastIndex) {
                var remainder = selstring.substring(lastIndex);
                fluid.fail("Error in selector string - can not match child selector expression at " + remainder);
            }
            if (childMatch[1] === ">") {
                fullAtNode.child = true;
            }
            togo[togo.length] = fullAtNode;
            // >= test here to compensate for IE bug http://blog.stevenlevithan.com/archives/exec-bugs
            if (childSeg.lastIndex >= selstring.length) {
                break;
            }
            lastIndex = childSeg.lastIndex;
            quickClass.lastIndex = childSeg.lastIndex; 
        }
        return togo;
    };
      
})(jQuery, fluid_1_5);
/*
Copyright 2008-2010 University of Cambridge
Copyright 2008-2009 University of Toronto
Copyright 2010-2011 Lucendo Development Ltd.

Licensed under the Educational Community License (ECL), Version 2.0 or the New
BSD license. You may not use this file except in compliance with one these
Licenses.

You may obtain a copy of the ECL 2.0 License and BSD License at
https://github.com/fluid-project/infusion/raw/master/Infusion-LICENSE.txt
*/

// Declare dependencies
/*global fluid_1_5:true, jQuery*/

// JSLint options 
/*jslint white: true, funcinvoke: true, continue: true, elsecatch: true, operator: true, jslintok:true, undef: true, newcap: true, regexp: true, bitwise: true, browser: true, forin: true, maxerr: 100, indent: 4 */

fluid_1_5 = fluid_1_5 || {};

(function ($, fluid) {
  
    function debugPosition(component) {
        return "as child of " + (component.parent.fullID ? "component with full ID " + component.parent.fullID : "root");
    }
     
    function computeFullID(component) {
        var togo = "";
        var move = component;
        if (component.children === undefined) { // not a container
            // unusual case on the client-side, since a repetitive leaf may have localID blasted onto it.
            togo = component.ID + (component.localID !== undefined ? component.localID : "");
            move = component.parent;
        }
        
        while (move.parent) {
            var parent = move.parent;
            if (move.fullID !== undefined) {
                togo = move.fullID + togo;
                return togo;
            }
            if (move.noID === undefined) {
                var ID = move.ID;
                if (ID === undefined) {
                    fluid.fail("Error in component tree - component found with no ID " +
                        debugPosition(parent) + ": please check structure");
                }
                var colpos = ID.indexOf(":");
                var prefix = colpos === -1 ? ID : ID.substring(0, colpos);
                togo = prefix + ":" + (move.localID === undefined ? "" : move.localID) + ":" + togo;
            }
            move = parent;
        }
        
        return togo;
    }

    var renderer = {};
  
    renderer.isBoundPrimitive = function (value) {
        return fluid.isPrimitive(value) || value instanceof Array 
            && (value.length === 0 || typeof (value[0]) === "string"); // jslint:ok
    };
  
    var unzipComponent;
  
    function processChild(value, key) {
        if (renderer.isBoundPrimitive(value)) {
            return {componentType: "UIBound", value: value, ID: key};
        } 
        else {
            var unzip = unzipComponent(value);
            if (unzip.ID) {
                return {ID: key, componentType: "UIContainer", children: [unzip]};
            } else {
                unzip.ID = key;
                return unzip;
            } 
        }
    }
  
    function fixChildren(children) {
        if (!(children instanceof Array)) {
            var togo = [];
            for (var key in children) {
                var value = children[key];
                if (value instanceof Array) {
                    for (var i = 0; i < value.length; ++i) {
                        var processed = processChild(value[i], key);
          //            if (processed.componentType === "UIContainer" &&
          //              processed.localID === undefined) {
          //              processed.localID = i;
          //            }
                        togo[togo.length] = processed;
                    }
                } else {
                    togo[togo.length] = processChild(value, key);
                } 
            }
            return togo;
        } else {return children; }
    }
  
    function fixupValue(uibound, model, resolverGetConfig) {
        if (uibound.value === undefined && uibound.valuebinding !== undefined) {
            if (!model) {
                fluid.fail("Cannot perform value fixup for valuebinding " 
                    + uibound.valuebinding + " since no model was supplied to rendering");
            }
            uibound.value = fluid.get(model, uibound.valuebinding, resolverGetConfig);
        }
    }
  
    function upgradeBound(holder, property, model, resolverGetConfig) {
        if (holder[property] !== undefined) {
            if (renderer.isBoundPrimitive(holder[property])) {
                holder[property] = {value: holder[property]};
            }
            else if (holder[property].messagekey) {
                holder[property].componentType = "UIMessage";
            }
        }
        else {
            holder[property] = {value: null};
        }
        fixupValue(holder[property], model, resolverGetConfig);
    }
  
    renderer.duckMap = {children: "UIContainer", 
            value: "UIBound", valuebinding: "UIBound", messagekey: "UIMessage", 
            markup: "UIVerbatim", selection: "UISelect", target: "UILink",
            choiceindex: "UISelectChoice", functionname: "UIInitBlock"};
      
    var boundMap = {
        UISelect:   ["selection", "optionlist", "optionnames"],
        UILink:     ["target", "linktext"],
        UIVerbatim: ["markup"],
        UIMessage:  ["messagekey"]
    };
  
    renderer.boundMap = fluid.transform(boundMap, fluid.arrayToHash);
      
    renderer.inferComponentType = function (component) {
        for (var key in renderer.duckMap) {
            if (component[key] !== undefined) {
                return renderer.duckMap[key];
            }
        }
    };
  
    renderer.applyComponentType = function (component) {
        component.componentType = renderer.inferComponentType(component);
        if (component.componentType === undefined && component.ID !== undefined) {
            component.componentType = "UIBound";
        }
    };
    
    unzipComponent = function (component, model, resolverGetConfig) {
        if (component) {
            renderer.applyComponentType(component);
        }
        if (!component || component.componentType === undefined) {
            var decorators = component.decorators;
            if (decorators) {delete component.decorators;}
            component = {componentType: "UIContainer", children: component};
            component.decorators = decorators;
        }
        var cType = component.componentType;
        if (cType === "UIContainer") {
            component.children = fixChildren(component.children);
        }
        else {
            var map = renderer.boundMap[cType];
            if (map) {
                fluid.each(map, function (value, key) {
                    upgradeBound(component, key, model, resolverGetConfig);
                });
            }
        }
        
        return component;
    };
    
    function fixupTree(tree, model, resolverGetConfig) {
        if (tree.componentType === undefined) {
            tree = unzipComponent(tree, model, resolverGetConfig);
        }
        if (tree.componentType !== "UIContainer" && !tree.parent) {
            tree = {children: [tree]};
        }
        
        if (tree.children) {
            tree.childmap = {};
            for (var i = 0; i < tree.children.length; ++i) {
                var child = tree.children[i];
                if (child.componentType === undefined) {
                    child = unzipComponent(child, model, resolverGetConfig);
                    tree.children[i] = child;
                }
                child.parent = tree;
                if (child.ID === undefined) {
                    fluid.fail("Error in component tree: component found with no ID " + debugPosition(child));
                }
                tree.childmap[child.ID] = child;
                var colpos = child.ID.indexOf(":"); 
                if (colpos === -1) {
                //  tree.childmap[child.ID] = child; // moved out of branch to allow
                // "relative id expressions" to be easily parsed
                }
                else { // jslint:ok - TODO: review the above
                    var prefix = child.ID.substring(0, colpos);
                    var childlist = tree.childmap[prefix]; 
                    if (!childlist) {
                        childlist = [];
                        tree.childmap[prefix] = childlist;
                    }
                    if (child.localID === undefined && childlist.length !== 0) {
                        child.localID = childlist.length;
                    }
                    childlist[childlist.length] = child;
                }
                child.fullID = computeFullID(child);
        
                var componentType = child.componentType;
                if (componentType === "UISelect") {
                    child.selection.fullID = child.fullID + "-selection";
                }
                else if (componentType === "UIInitBlock") {
                    var call = child.functionname + '(';
                    for (var j = 0; j < child.arguments.length; ++j) { // jslint:ok
                        if (child.arguments[j] instanceof fluid.ComponentReference) { // jslint:ok
                            // TODO: support more forms of id reference
                            child.arguments[j] = child.parent.fullID + child.arguments[j].reference; // jslint:ok
                        }
                        call += JSON.stringify(child.arguments[j]); // jslint:ok
                        if (j < child.arguments.length - 1) { // jslint:ok
                            call += ", ";
                        }
                    }
                    child.markup = {value: call + ")\n"};
                    child.componentType = "UIVerbatim";
                }
                else if (componentType === "UIBound") {
                    fixupValue(child, model, resolverGetConfig);
                }
                fixupTree(child, model, resolverGetConfig);
            }
        }
        return tree;
    }
    
    fluid.NULL_STRING = "\u25a9null\u25a9";
  
    var LINK_ATTRIBUTES = {
        a: "href", link: "href", img: "src", frame: "src", script: "src", style: "src", input: "src", embed: "src", // jslint:ok
        form: "action",
        applet: "codebase", object: "codebase" //jslint:ok
    };
    
    renderer.decoratorComponentPrefix = "**-renderer-";
  
    renderer.IDtoComponentName = function(ID, num) {
        return renderer.decoratorComponentPrefix + ID.replace(/\./g, "") + "-" + num;
    };
    
    renderer.invokeFluidDecorator = function(func, args, ID, num, options) {
        var that;
        if (options.instantiator && options.parentComponent) {
            var parent = options.parentComponent;
            var name = renderer.IDtoComponentName(ID, num);
            // TODO: The best we can do here without GRADES is to wildly guess 
            // that it is a view component with options in the 2nd place and container in first place
            fluid.set(parent, fluid.path("options", "components", name), {type: func});
            // This MIGHT really be a variant of fluid.invoke... only we often probably DO want the component
            // itself to be inserted into the that stack. This *ALSO* requires GRADES to resolve. A 
            // "function" is that which has no grade. The gradeless grade.
            that = fluid.initDependent(options.parentComponent, name, options.instantiator, args);
        }
        else {
            that = fluid.invokeGlobalFunction(func, args);
        }
        return that;
    };
  
    fluid.renderer = function (templates, tree, options, fossilsIn) {
      
        options = options || {};
        tree = tree || {};
        var debugMode = options.debugMode;
        if (!options.messageLocator && options.messageSource) {
            options.messageLocator = fluid.resolveMessageSource(options.messageSource);
        }
        options.document = options.document || document;
        options.jQuery = options.jQuery || $;
        options.fossils = options.fossils || fossilsIn || {}; // map of submittingname to {EL, submittingname, oldvalue}
      
        var globalmap = {};
        var branchmap = {};
        var rewritemap = {}; // map of rewritekey (for original id in template) to full ID 
        var seenset = {};
        var collected = {};
        var out = "";
        var renderOptions = options;
        var decoratorQueue = [];
        
        var renderedbindings = {}; // map of fullID to true for UISelects which have already had bindings written
        var usedIDs = {};
        
        var that = {options: options};
        
        function getRewriteKey(template, parent, id) {
            return template.resourceKey + parent.fullID + id;
        }
        // returns: lump
        function resolveInScope(searchID, defprefix, scope, child) {
            var deflump;
            var scopelook = scope? scope[searchID] : null;
            if (scopelook) {
                for (var i = 0; i < scopelook.length; ++i) {
                    var scopelump = scopelook[i];
                    if (!deflump && scopelump.rsfID === defprefix) {
                        deflump = scopelump;
                    }
                    if (scopelump.rsfID === searchID) {
                        return scopelump;
                    }
                }
            }
            return deflump;
        }
        // returns: lump
        function resolveCall(sourcescope, child) {
            var searchID = child.jointID? child.jointID : child.ID;
            var split = fluid.SplitID(searchID);
            var defprefix = split.prefix + ':';
            var match = resolveInScope(searchID, defprefix, sourcescope.downmap, child);
            if (match) {return match;}
            if (child.children) {
                match = resolveInScope(searchID, defprefix, globalmap, child);
                if (match) {return match;}
            }
            return null;
        }
        
        function noteCollected(template) {
            if (!seenset[template.href]) {
                fluid.aggregateMMap(collected, template.collectmap);
                seenset[template.href] = true;
            }
        }
        
        var fetchComponent;
        
        function resolveRecurse(basecontainer, parentlump) {
            for (var i = 0; i < basecontainer.children.length; ++i) {
                var branch = basecontainer.children[i];
                if (branch.children) { // it is a branch
                    var resolved = resolveCall(parentlump, branch);
                    if (resolved) {
                        branchmap[branch.fullID] = resolved;
                        var id = resolved.attributemap.id;
                        if (id !== undefined) {
                            rewritemap[getRewriteKey(parentlump.parent, basecontainer, id)] = branch.fullID;
                        }
                        // on server-side this is done separately
                        noteCollected(resolved.parent);
                        resolveRecurse(branch, resolved);
                    }
                }
            }
            // collect any rewritten ids for the purpose of later rewriting
            if (parentlump.downmap) {
                for (var id in parentlump.downmap) { // jslint:ok - scoping
                  //if (id.indexOf(":") === -1) {
                    var lumps = parentlump.downmap[id];
                    for (var i = 0; i < lumps.length; ++i) { // jslint:ok - scoping
                        var lump = lumps[i];
                        var lumpid = lump.attributemap.id;
                        if (lumpid !== undefined && lump.rsfID !== undefined) {
                            var resolved = fetchComponent(basecontainer, lump.rsfID); //jslint:ok - scoping
                            if (resolved !== null) {
                                var resolveID = resolved.fullID;
                                if (resolved.componentType === "UISelect") {
                                    resolveID = resolveID + "-selection";
                                }
                                rewritemap[getRewriteKey(parentlump.parent, basecontainer,
                                    lumpid)] = resolveID;
                            }
                        }
                    }
                //  }
                } 
            }
            
        }
        
        function resolveBranches(globalmapp, basecontainer, parentlump) {
            branchmap = {};
            rewritemap = {};
            seenset = {};
            collected = {};
            globalmap = globalmapp;
            branchmap[basecontainer.fullID] = parentlump;
            resolveRecurse(basecontainer, parentlump);
        }
               
        function dumpTillLump(lumps, start, limit) {
            for (; start < limit; ++start) {
                var text = lumps[start].text;
                if (text) { // guard against "undefined" lumps from "justended"
                    out += lumps[start].text;
                }
            }
        }
      
        function dumpScan(lumps, renderindex, basedepth, closeparent, insideleaf) {
            var start = renderindex;
            while (true) {
                if (renderindex === lumps.length) {
                    break;
                }
                var lump = lumps[renderindex];
                if (lump.nestingdepth < basedepth) {
                    break;
                }
                if (lump.rsfID !== undefined) {
                    if (!insideleaf) {break;}
                    if (insideleaf && lump.nestingdepth > basedepth + (closeparent? 0 : 1)) {
                        fluid.log("Error in component tree - leaf component found to contain further components - at " +
                            lump.toString());
                    }
                    else {break;}
                }
                // target.print(lump.text);
                ++renderindex;
            }
            // ASSUMPTIONS: close tags are ONE LUMP
            if (!closeparent && (renderindex === lumps.length || !lumps[renderindex].rsfID)) {
                --renderindex;
            }
            
            dumpTillLump(lumps, start, renderindex);
            //target.write(buffer, start, limit - start);
            return renderindex;
        }
        
        
        function isPlaceholder(value) {
            // TODO: equivalent of server-side "placeholder" system
            return false;
        }
        
        function isValue(value) {
            return value !== null && value !== undefined && !isPlaceholder(value);
        }
        
        // In RSF Client, this is a "flyweight" "global" object that is reused for every tag, 
        // to avoid generating garbage. In RSF Server, it is an argument to the following rendering
        // methods of type "TagRenderContext".
        
        var trc = {};
        
        /*** TRC METHODS ***/
        
        function openTag() {
            if (!trc.iselide) {
                out += "<" + trc.uselump.tagname;
            }
        }
        
        function closeTag() {
            if (!trc.iselide) {
                out += "</" + trc.uselump.tagname + ">";
            }
        }
      
        function renderUnchanged() {
            // TODO needs work since we don't keep attributes in text
            dumpTillLump(trc.uselump.parent.lumps, trc.uselump.lumpindex + 1,
                trc.close.lumpindex + (trc.iselide ? 0 : 1));
        }

        function isSelfClose() {
            return trc.endopen.lumpindex === trc.close.lumpindex && fluid.XMLP.closedTags[trc.uselump.tagname]; 
        }

        function dumpTemplateBody() {
            if (isSelfClose()) {
                if (!trc.iselide) {
                    out += "/>";
                }
            }
            else {
                if (!trc.iselide) {
                    out += ">";
                }
                dumpTillLump(trc.uselump.parent.lumps, trc.endopen.lumpindex,
                    trc.close.lumpindex + (trc.iselide ? 0 : 1));
            }
        }
        
        function replaceAttributes() {
            if (!trc.iselide) {
                out += fluid.dumpAttributes(trc.attrcopy);
            }
            dumpTemplateBody();
        }
      
        function replaceAttributesOpen() {
            if (trc.iselide) {
                replaceAttributes();
            }
            else {
                out += fluid.dumpAttributes(trc.attrcopy);
                var selfClose = isSelfClose();
                // TODO: the parser does not ever produce empty tags
                out += selfClose ? "/>" : ">";
          
                trc.nextpos = selfClose? trc.close.lumpindex + 1 : trc.endopen.lumpindex;
            }
        }

        function replaceBody(value) {
            out += fluid.dumpAttributes(trc.attrcopy);
            if (!trc.iselide) {
                out += ">";
            }
            out += fluid.XMLEncode(value.toString());
            closeTag();
        }
      
        function rewriteLeaf(value) {
            if (isValue(value)) {
                replaceBody(value);
            }
            else {
                replaceAttributes();
            }
        }
      
        function rewriteLeafOpen(value) {
            if (trc.iselide) {
                rewriteLeaf(trc.value);
            }
            else {
                if (isValue(value)) {
                    replaceBody(value);
                }
                else {
                    replaceAttributesOpen();
                }
            }
        }

        
        /*** END TRC METHODS**/
        
        function rewriteUrl(template, url) {
            if (renderOptions.urlRewriter) {
                var rewritten = renderOptions.urlRewriter(url);
                if (rewritten) {
                    return rewritten;
                }
            }
            if (!renderOptions.rebaseURLs) {
                return url;
            }
            var protpos = url.indexOf(":/");
            if (url.charAt(0) === '/' || protpos !== -1 && protpos < 7) { // jslint:ok
                return url;
            }
            else {
                return renderOptions.baseURL + url;
            }
        }
        
        function dumpHiddenField(/** UIParameter **/ todump) { // jslint:ok
            out += "<input type=\"hidden\" ";
            var isvirtual = todump.virtual;
            var outattrs = {};
            outattrs[isvirtual? "id" : "name"] = todump.name;
            outattrs.value = todump.value;
            out += fluid.dumpAttributes(outattrs);
            out += " />\n";
        }
        
        var outDecoratorsImpl;
        
        function applyAutoBind(torender, finalID) {
            if (!finalID) {
              // if no id is assigned so far, this is a signal that this is a "virtual" component such as
              // a non-HTML UISelect which will not have physical markup.
                return; 
            }
            var tagname = trc.uselump.tagname;
            var applier = renderOptions.applier;
            function applyFunc() {
                fluid.applyBoundChange(fluid.byId(finalID, renderOptions.document), undefined, applier);
            }
            if (renderOptions.autoBind && /input|select|textarea/.test(tagname) 
                    && !renderedbindings[finalID]) {
                var decorators = [{jQuery: ["change", applyFunc]}];
                // Work around bug 193: http://webbugtrack.blogspot.com/2007/11/bug-193-onchange-does-not-fire-properly.html
                if ($.browser.msie && tagname === "input" 
                        && /radio|checkbox/.test(trc.attrcopy.type)) {
                    decorators.push({jQuery: ["click", applyFunc]});
                }
                if ($.browser.safari && tagname === "input" && trc.attrcopy.type === "radio") {
                    decorators.push({jQuery: ["keyup", applyFunc]});
                }
                outDecoratorsImpl(torender, decorators, trc.attrcopy, finalID); // jslint:ok - forward reference
            }    
        }
        
        function dumpBoundFields(/** UIBound**/ torender, parent) { // jslint:ok - whitespace
            if (torender) {
                var holder = parent? parent : torender;
                if (renderOptions.fossils && holder.valuebinding) {
                    var fossilKey = holder.submittingname || torender.finalID;
                  // TODO: this will store multiple times for each member of a UISelect
                    renderOptions.fossils[fossilKey] = {
                        name: fossilKey,
                        EL: holder.valuebinding,
                        oldvalue: holder.value
                    };
                  // But this has to happen multiple times
                    applyAutoBind(torender, torender.finalID);
                }
                if (torender.fossilizedbinding) {
                    dumpHiddenField(torender.fossilizedbinding);
                }
                if (torender.fossilizedshaper) {
                    dumpHiddenField(torender.fossilizedshaper);
                }
            }
        }
        
        function dumpSelectionBindings(uiselect) {
            if (!renderedbindings[uiselect.selection.fullID]) {
                renderedbindings[uiselect.selection.fullID] = true; // set this true early so that selection does not autobind twice
                dumpBoundFields(uiselect.selection);
                dumpBoundFields(uiselect.optionlist);
                dumpBoundFields(uiselect.optionnames);
            }
        }
          
        function isSelectedValue(torender, value) {
            var selection = torender.selection;
            return selection.value && typeof(selection.value) !== "string" && typeof(selection.value.length) === "number" ? 
                $.inArray(value, selection.value, value) !== -1 :
                selection.value === value;
        }
        
        function getRelativeComponent(component, relativeID) {
            component = component.parent;
            while (relativeID.indexOf("..::") === 0) {
                relativeID = relativeID.substring(4);
                component = component.parent;
            }
            return component.childmap[relativeID];
        }
        
        function adjustForID(attrcopy, component, late, forceID) {
            if (!late) {
                delete attrcopy["rsf:id"];
            }
            if (component.finalID !== undefined) {
                attrcopy.id = component.finalID;
            }
            else if (forceID !== undefined) {
                attrcopy.id = forceID;
            }
            else {
                if (attrcopy.id || late) {
                    attrcopy.id = component.fullID;
                }
            }
            
            var count = 1;
            var baseid = attrcopy.id;
            while (renderOptions.document.getElementById(attrcopy.id) || usedIDs[attrcopy.id]) {
                attrcopy.id = baseid + "-" + (count++); 
            }
            component.finalID = attrcopy.id;
            return attrcopy.id;
        }
        
        function assignSubmittingName(attrcopy, component, parent) {
            var submitting = parent || component;
          // if a submittingName is required, we must already go out to the document to 
          // uniquify the id that it will be derived from
            adjustForID(attrcopy, component, true, component.fullID);
            if (submitting.submittingname === undefined && submitting.willinput !== false) {
                submitting.submittingname = submitting.finalID || submitting.fullID;
            }
            return submitting.submittingname;
        }
             
        function explodeDecorators(decorators) {
            var togo = [];
            if (decorators.type) {
                togo[0] = decorators;
            }
            else {
                for (var key in decorators) {
                    if (key === "$") {key = "jQuery";}
                    var value = decorators[key];
                    var decorator = {
                        type: key
                    };
                    if (key === "jQuery") {
                        decorator.func = value[0];
                        decorator.args = value.slice(1);
                    }
                    else if (key === "addClass" || key === "removeClass") {
                        decorator.classes = value;
                    }
                    else if (key === "attrs") {
                        decorator.attributes = value;
                    }
                    else if (key === "identify") {
                        decorator.key = value;
                    }
                    togo[togo.length] = decorator;
                }
            }
            return togo;
        }
        
        outDecoratorsImpl = function(torender, decorators, attrcopy, finalID) {
            renderOptions.idMap = renderOptions.idMap || {};
            for (var i = 0; i < decorators.length; ++i) {
                var decorator = decorators[i];
                var type = decorator.type;
                if (!type) {
                    var explodedDecorators = explodeDecorators(decorator);
                    outDecoratorsImpl(torender, explodedDecorators, attrcopy, finalID);
                    continue;
                }
                if (type === "$") {type = decorator.type = "jQuery";}
                if (type === "jQuery" || type === "event" || type === "fluid") {
                    var id = adjustForID(attrcopy, torender, true, finalID);
                    if (decorator.ids === undefined) {
                        decorator.ids = [];
                        decoratorQueue[decoratorQueue.length] = decorator; 
                    }
                    decorator.ids.push(id);
                }
                // honour these remaining types immediately
                else if (type === "attrs") {
                    fluid.each(decorator.attributes, function(value, key) {
                        if (value === null || value === undefined) {
                            delete attrcopy[key];
                        }
                        else {
                            attrcopy[key] = fluid.XMLEncode(value);
                        }
                    }); // jslint:ok - function within loop
                }
                else if (type === "addClass" || type === "removeClass") {
                    var fakeNode = {
                        nodeType: 1,
                        className: attrcopy["class"] || ""
                    };
                    renderOptions.jQuery(fakeNode)[type](decorator.classes);
                    attrcopy["class"] = fakeNode.className;
                }
                else if (type === "identify") {
                    var id = adjustForID(attrcopy, torender, true, finalID); // jslint:ok - scoping
                    renderOptions.idMap[decorator.key] = id;
                }
                else if (type !== "null") {
                    fluid.log("Unrecognised decorator of type " + type + " found at component of ID " + finalID);
                }
            }
        };
        
        function outDecorators(torender, attrcopy) {
            if (!torender.decorators) {return;}
            if (torender.decorators.length === undefined) {
                torender.decorators = explodeDecorators(torender.decorators);
            }
            outDecoratorsImpl(torender, torender.decorators, attrcopy);
        }
        
        function dumpBranchHead(branch, targetlump) {
            if (targetlump.elide) {
                return;
            }
            var attrcopy = {};
            $.extend(true, attrcopy, targetlump.attributemap);
            adjustForID(attrcopy, branch); // jslint:ok - forward reference
            outDecorators(branch, attrcopy);
            out += "<" + targetlump.tagname + " ";
            out += fluid.dumpAttributes(attrcopy);
            out += ">";
        }
        
        function resolveArgs(args) {
            if (!args) {return args;}
            return fluid.transform(args, function (arg, index) {
                upgradeBound(args, index, renderOptions.model, renderOptions.resolverGetConfig);
                return args[index].value;
            });
        }
            
        function degradeMessage(torender) {
            if (torender.componentType === "UIMessage") {
                // degrade UIMessage to UIBound by resolving the message
                torender.componentType = "UIBound";
                if (!renderOptions.messageLocator) {
                    torender.value = "[No messageLocator is configured in options - please consult documentation on options.messageSource]";
                }
                else {
                    upgradeBound(torender, "messagekey", renderOptions.model, renderOptions.resolverGetConfig);
                    var resArgs = resolveArgs(torender.args);
                    torender.value = renderOptions.messageLocator(torender.messagekey.value, resArgs);
                }
            }
        }  
        
          
        function renderComponent(torender) {
            var attrcopy = trc.attrcopy;
            
            degradeMessage(torender);
            var componentType = torender.componentType;
            var tagname = trc.uselump.tagname;
            
            outDecorators(torender, attrcopy);
            
            function makeFail(torender, end) {
                fluid.fail("Error in component tree - UISelectChoice with id " + torender.fullID + end);
            } 
            
            if (componentType === "UIBound" || componentType === "UISelectChoice") {
                var parent;
                if (torender.choiceindex !== undefined) {
                    if (torender.parentRelativeID !== undefined) {
                        parent = getRelativeComponent(torender, torender.parentRelativeID);
                        if (!parent) {
                            makeFail(torender, " has parentRelativeID of " + torender.parentRelativeID + " which cannot be resolved");
                        }
                    }
                    else {
                        makeFail(torender, " does not have parentRelativeID set");
                    }
                    assignSubmittingName(attrcopy, torender, parent.selection);
                    dumpSelectionBindings(parent);
                }
        
                var submittingname = parent? parent.selection.submittingname : torender.submittingname;
                if (!parent && torender.valuebinding) {
                    // Do this for all bound fields even if non submitting so that finalID is set in order to track fossils (FLUID-3387)
                    submittingname = assignSubmittingName(attrcopy, torender);
                }
                if (tagname === "input" || tagname === "textarea") {
                    if (submittingname !== undefined) {
                        attrcopy.name = submittingname;
                    }
                }
                // this needs to happen early on the client, since it may cause the allocation of the
                // id in the case of a "deferred decorator". However, for server-side bindings, this 
                // will be an inappropriate time, unless we shift the timing of emitting the opening tag.
                dumpBoundFields(torender, parent? parent.selection : null);
          
                if (typeof(torender.value) === 'boolean' || attrcopy.type === "radio" 
                        || attrcopy.type === "checkbox") {
                    var underlyingValue;
                    var directValue = torender.value;
                    
                    if (torender.choiceindex !== undefined) {
                        if (!parent.optionlist.value) {
                            fluid.fail("Error in component tree - selection control with full ID " + parent.fullID + " has no values");
                        }
                        underlyingValue = parent.optionlist.value[torender.choiceindex];
                        directValue = isSelectedValue(parent, underlyingValue);
                    }
                    if (isValue(directValue)) {
                        if (directValue) {
                            attrcopy.checked = "checked";
                        }
                        else {
                            delete attrcopy.checked;
                        }
                    }
                    attrcopy.value = fluid.XMLEncode(underlyingValue? underlyingValue : "true");
                    rewriteLeaf(null);
                }
                else if (torender.value instanceof Array) {
                    // Cannot be rendered directly, must be fake
                    renderUnchanged();
                }
                else { // String value
                    var value = parent? 
                        parent[tagname === "textarea" || tagname === "input" ? "optionlist" : "optionnames"].value[torender.choiceindex] : 
                            torender.value; // jslint:ok - whitespace
                    if (tagname === "textarea") {
                        if (isPlaceholder(value) && torender.willinput) {
                            // FORCE a blank value for input components if nothing from
                            // model, if input was intended.
                            value = "";
                        }
                        rewriteLeaf(value);
                    }
                    else if (tagname === "input") {
                        if (torender.willinput || isValue(value)) {
                            attrcopy.value = fluid.XMLEncode(String(value));
                        }
                        rewriteLeaf(null);
                    }
                    else {
                        delete attrcopy.name;
                        rewriteLeafOpen(value);
                    }
                }
            }
            else if (componentType === "UISelect") {
  
                var ishtmlselect = tagname === "select";
                var ismultiple = false;
          
                if (torender.selection.value instanceof Array) {
                    ismultiple = true;
                    if (ishtmlselect) {
                        attrcopy.multiple = "multiple";
                    }
                }
                // assignSubmittingName is now the definitive trigger point for uniquifying output IDs
                // However, if id is already assigned it is probably through attempt to decorate root select.
                // in this case restore it.
                var oldid = attrcopy.id;
                assignSubmittingName(attrcopy, torender.selection);
                if (oldid !== undefined) {
                    attrcopy.id = oldid;
                }
                
                if (ishtmlselect) {
                    // The HTML submitted value from a <select> actually corresponds
                    // with the selection member, not the top-level component.
                    if (torender.selection.willinput !== false) {
                        attrcopy.name = torender.selection.submittingname;
                    }
                    applyAutoBind(torender, attrcopy.id);
                }
                
                out += fluid.dumpAttributes(attrcopy);
                if (ishtmlselect) {
                    out += ">";
                    var values = torender.optionlist.value;
                    var names = torender.optionnames === null || torender.optionnames === undefined || !torender.optionnames.value? values : torender.optionnames.value;
                    if (!names || !names.length) {
                        fluid.fail("Error in component tree - UISelect component with fullID " 
                            + torender.fullID + " does not have optionnames set");
                    }
                    for (var i = 0; i < names.length; ++i) {
                        out += "<option value=\"";
                        var value = values[i]; //jslint:ok - scoping
                        if (value === null) {
                            value = fluid.NULL_STRING;
                        }
                        out += fluid.XMLEncode(value);
                        if (isSelectedValue(torender, value)) {
                            out += "\" selected=\"selected";
                        }
                        out += "\">";
                        out += fluid.XMLEncode(names[i]);
                        out += "</option>\n";
                    }
                    closeTag();
                }
                else {
                    dumpTemplateBody();
                }
                dumpSelectionBindings(torender);
            }
            else if (componentType === "UILink") {
                var attrname = LINK_ATTRIBUTES[tagname];
                if (attrname) {
                    degradeMessage(torender.target);
                    var target = torender.target.value;
                    if (!isValue(target)) {
                        target = attrcopy[attrname];
                    }
                    target = rewriteUrl(trc.uselump.parent, target);
                    // Note that all real browsers succeed in recovering the URL here even if it is presented in violation of XML
                    // seemingly due to the purest accident, the text &amp; cannot occur in a properly encoded URL :P
                    attrcopy[attrname] = fluid.XMLEncode(target);
                }
                var value; // jslint:ok
                if (torender.linktext) { 
                    degradeMessage(torender.linktext);
                    value = torender.linktext.value; // jslint:ok - scoping
                }
                if (!isValue(value)) {
                    replaceAttributesOpen();
                }
                else {
                    rewriteLeaf(value);
                }
            }
            
            else if (torender.markup !== undefined) { // detect UIVerbatim
                degradeMessage(torender.markup);
                var rendered = torender.markup.value;
                if (rendered === null) {
                  // TODO, doesn't quite work due to attr folding cf Java code
                    out += fluid.dumpAttributes(attrcopy);
                    out += ">";
                    renderUnchanged(); 
                }
                else {
                    if (!trc.iselide) {
                        out += fluid.dumpAttributes(attrcopy);
                        out += ">";
                    }
                    out += rendered;
                    closeTag();
                }
            }
            if (attrcopy.id !== undefined) {
                usedIDs[attrcopy.id] = true;
            }
        }
             
        function rewriteIDRelation(context) {
            var attrname;
            var attrval = trc.attrcopy["for"];
            if (attrval !== undefined) {
                attrname = "for";
            }
            else {
                attrval = trc.attrcopy.headers;
                if (attrval !== undefined) {
                    attrname = "headers";
                }
            }
            if (!attrname) {return;}
            var tagname = trc.uselump.tagname;
            if (attrname === "for" && tagname !== "label") {return;}
            if (attrname === "headers" && tagname !== "td" && tagname !== "th") {return;}
            var rewritten = rewritemap[getRewriteKey(trc.uselump.parent, context, attrval)];
            if (rewritten !== undefined) {
                trc.attrcopy[attrname] = rewritten;
            }
        }
        
        function renderComment(message) {
            out += ("<!-- " + fluid.XMLEncode(message) + "-->");
        }
        
        function renderDebugMessage(message) {
            out += "<span style=\"background-color:#FF466B;color:white;padding:1px;\">";
            out += message;
            out += "</span><br/>";
        }
        
        function reportPath(/*UIComponent*/ branch) { // jslint:ok - whitespace
            var path = branch.fullID;
            return !path ? "component tree root" : "full path " + path;
        }
        
        function renderComponentSystem(context, torendero, lump) {
            var lumpindex = lump.lumpindex;
            var lumps = lump.parent.lumps;
            var nextpos = -1;
            var outerendopen = lumps[lumpindex + 1];
            var outerclose = lump.close_tag;
        
            nextpos = outerclose.lumpindex + 1;
        
            var payloadlist = lump.downmap? lump.downmap["payload-component"] : null;
            var payload = payloadlist? payloadlist[0] : null;
            
            var iselide = lump.rsfID.charCodeAt(0) === 126; // "~"
            
            var endopen = outerendopen;
            var close = outerclose;
            var uselump = lump;
            var attrcopy = {};
            $.extend(true, attrcopy, (payload === null? lump : payload).attributemap);
            
            trc.attrcopy = attrcopy;
            trc.uselump = uselump;
            trc.endopen = endopen;
            trc.close = close;
            trc.nextpos = nextpos;
            trc.iselide = iselide;
            
            rewriteIDRelation(context);
            
            if (torendero === null) {
                if (lump.rsfID.indexOf("scr=") === (iselide? 1 : 0)) {
                    var scrname = lump.rsfID.substring(4 + (iselide? 1 : 0));
                    if (scrname === "ignore") {
                        nextpos = trc.close.lumpindex + 1;
                    }
                    else if (scrname === "rewrite-url") {
                        torendero = {componentType: "UILink", target: {}};
                    }
                    else {
                        openTag();
                        replaceAttributesOpen();
                        nextpos = trc.endopen.lumpindex;
                    }
                }
            }
            if (torendero !== null) {
                // else there IS a component and we are going to render it. First make
                // sure we render any preamble.
          
                if (payload) {
                    trc.endopen = lumps[payload.lumpindex + 1];
                    trc.close = payload.close_tag;
                    trc.uselump = payload;
                    dumpTillLump(lumps, lumpindex, payload.lumpindex);
                    lumpindex = payload.lumpindex;
                }
          
                adjustForID(attrcopy, torendero);
                //decoratormanager.decorate(torendero.decorators, uselump.getTag(), attrcopy);
          
                
                // ALWAYS dump the tag name, this can never be rewritten. (probably?!)
                openTag();
          
                renderComponent(torendero);
                // if there is a payload, dump the postamble.
                if (payload !== null) {
                    // the default case is initialised to tag close
                    if (trc.nextpos === nextpos) {
                        dumpTillLump(lumps, trc.close.lumpindex + 1, outerclose.lumpindex + 1);
                    }
                }
                nextpos = trc.nextpos;
            }
            return nextpos;
        }
        var renderRecurse;
        
        function renderContainer(child, targetlump) {
            var t2 = targetlump.parent;
            var firstchild = t2.lumps[targetlump.lumpindex + 1];
            if (child.children !== undefined) {
                dumpBranchHead(child, targetlump);
            }
            else {
                renderComponentSystem(child.parent, child, targetlump);
            }
            renderRecurse(child, targetlump, firstchild);
        }
        
        fetchComponent = function(basecontainer, id, lump) {
            if (id.indexOf("msg=") === 0) {
                var key = id.substring(4);
                return {componentType: "UIMessage", messagekey: key};
            }
            while (basecontainer) {
                var togo = basecontainer.childmap[id];
                if (togo) {
                    return togo;
                }
                basecontainer = basecontainer.parent;
            }
            return null;
        };
      
        function fetchComponents(basecontainer, id) {
            var togo;
            while (basecontainer) {
                togo = basecontainer.childmap[id];
                if (togo) {
                    break;
                }
                basecontainer = basecontainer.parent;
            }
            return togo;
        }
      
        function findChild(sourcescope, child) {
            var split = fluid.SplitID(child.ID);
            var headlumps = sourcescope.downmap[child.ID];
            if (!headlumps) {
                headlumps = sourcescope.downmap[split.prefix + ":"];
            }
            return headlumps? headlumps[0] : null;
        }
        
        renderRecurse = function(basecontainer, parentlump, baselump) {
            var renderindex = baselump.lumpindex;
            var basedepth = parentlump.nestingdepth;
            var t1 = parentlump.parent;
            var rendered;
            if (debugMode) {
                rendered = {};
            }
            while (true) {
                renderindex = dumpScan(t1.lumps, renderindex, basedepth, !parentlump.elide, false);
                if (renderindex === t1.lumps.length) { 
                    break;
                }
                var lump = t1.lumps[renderindex];      
                var id = lump.rsfID;
                // new stopping rule - we may have been inside an elided tag
                if (lump.nestingdepth < basedepth || id === undefined) {
                    break;
                } 
          
                if (id.charCodeAt(0) === 126) { // "~"
                    id = id.substring(1);
                }
                
                //var ismessagefor = id.indexOf("message-for:") === 0;
                
                if (id.indexOf(':') !== -1) {
                    var prefix = fluid.getPrefix(id);
                    var children = fetchComponents(basecontainer, prefix);
                    
                    var finallump = lump.uplump.finallump[prefix];
                    var closefinal = finallump.close_tag;
                    
                    if (children) {
                        for (var i = 0; i < children.length; ++i) {
                            var child = children[i];
                            if (child.children) { // it is a branch 
                                if (debugMode) {
                                    rendered[child.fullID] = true;
                                }
                                var targetlump = branchmap[child.fullID];
                                if (targetlump) {
                                    if (debugMode) {
                                        renderComment("Branching for " + child.fullID + " from "
                                            + fluid.debugLump(lump) + " to " + fluid.debugLump(targetlump));
                                    }
                                    
                                    renderContainer(child, targetlump);
                                    
                                    if (debugMode) {
                                        renderComment("Branch returned for " + child.fullID
                                            + fluid.debugLump(lump) + " to " + fluid.debugLump(targetlump));
                                    }
                                }
                                else if (debugMode) {
                                    renderDebugMessage(
                                        "No matching template branch found for branch container with full ID "
                                            + child.fullID
                                            + " rendering from parent template branch "
                                            + fluid.debugLump(baselump)); // jslint:ok - line breaking
                                }
                            }
                            else { // repetitive leaf
                                var targetlump = findChild(parentlump, child); // jslint:ok - scoping
                                if (!targetlump) {
                                    if (debugMode) {
                                        renderDebugMessage("Repetitive leaf with full ID " + child.fullID
                                            + " could not be rendered from parent template branch "
                                            + fluid.debugLump(baselump)); // jslint:ok - line breaking
                                    }
                                    continue;
                                }
                                var renderend = renderComponentSystem(basecontainer, child, targetlump);
                                var wasopentag = renderend < t1.lumps.lengtn && t1.lumps[renderend].nestingdepth >= targetlump.nestingdepth;
                                var newbase = child.children? child : basecontainer;
                                if (wasopentag) {
                                    renderRecurse(newbase, targetlump, t1.lumps[renderend]);
                                    renderend = targetlump.close_tag.lumpindex + 1;
                                }
                                if (i !== children.length - 1) {
                                    // TODO - fix this bug in RSF Server!
                                    if (renderend < closefinal.lumpindex) {
                                        dumpScan(t1.lumps, renderend, targetlump.nestingdepth - 1, false, false);
                                    }
                                }
                                else {
                                    dumpScan(t1.lumps, renderend, targetlump.nestingdepth, true, false);
                                }
                            }
                        } // end for each repetitive child
                    }
                    else {
                        if (debugMode) {
                            renderDebugMessage("No branch container with prefix "
                                + prefix + ": found in container "
                                + reportPath(basecontainer)
                                + " rendering at template position " + fluid.debugLump(baselump)
                                + ", skipping");
                        }
                    }
                    
                    renderindex = closefinal.lumpindex + 1;
                    if (debugMode) {
                        renderComment("Stack returned from branch for ID " + id + " to "
                            + fluid.debugLump(baselump) + ": skipping from " + fluid.debugLump(lump)
                            + " to " + fluid.debugLump(closefinal));
                    }
                }
                else {
                    var component;
                    if (id) {
                        component = fetchComponent(basecontainer, id, lump);
                        if (debugMode && component) {
                            rendered[component.fullID] = true;
                        }
                    }
                    if (component && component.children !== undefined) {
                        renderContainer(component);
                        renderindex = lump.close_tag.lumpindex + 1;
                    }
                    else {
                        renderindex = renderComponentSystem(basecontainer, component, lump);
                    }
                }
                if (renderindex === t1.lumps.length) {
                    break;
                }
            }
            if (debugMode) {
                var children = basecontainer.children; // jslint:ok - scoping
                for (var key = 0; key < children.length; ++key) {
                    var child = children[key]; // jslint:ok - scoping
                    if (!rendered[child.fullID]) {
                        renderDebugMessage("Component "
                            + child.componentType + " with full ID "
                            + child.fullID + " could not be found within template "
                            + fluid.debugLump(baselump));
                    }
                }
            }  
            
        };
        
        function renderCollect(collump) {
            dumpTillLump(collump.parent.lumps, collump.lumpindex, collump.close_tag.lumpindex + 1);
        }
        
        // Let us pray
        function renderCollects() {
            for (var key in collected) {
                var collist = collected[key];
                for (var i = 0; i < collist.length; ++i) {
                    renderCollect(collist[i]);
                }
            }
        }
        
        function processDecoratorQueue() {
            for (var i = 0; i < decoratorQueue.length; ++i) {
                var decorator = decoratorQueue[i];
                for (var j = 0; j < decorator.ids.length; ++j) {
                    var id = decorator.ids[j];
                    var node = fluid.byId(id, renderOptions.document);
                    if (!node) {
                        fluid.fail("Error during rendering - component with id " + id 
                            + " which has a queued decorator was not found in the output markup");
                    }
                    if (decorator.type === "jQuery") {
                        var jnode = renderOptions.jQuery(node);
                        jnode[decorator.func].apply(jnode, fluid.makeArray(decorator.args));
                    }
                    else if (decorator.type === "fluid") {
                        var args = decorator.args;
                        if (!args) {
                            var thisContainer = renderOptions.jQuery(node);
                            if (!decorator.container) {
                                decorator.container = thisContainer;
                            }
                            else {
                                decorator.container.push(node);
                            }
                            args = [thisContainer, decorator.options];
                        }
                        var that = renderer.invokeFluidDecorator(decorator.func, args, id, i, options);
                        decorator.that = that;
                    }
                    else if (decorator.type === "event") {
                        node[decorator.event] = decorator.handler; 
                    }
                }
            }
        }
  
        that.renderTemplates = function () {
            tree = fixupTree(tree, options.model, options.resolverGetConfig);
            var template = templates[0];
            resolveBranches(templates.globalmap, tree, template.rootlump);
            renderedbindings = {};
            renderCollects();
            renderRecurse(tree, template.rootlump, template.lumps[template.firstdocumentindex]);
            return out;
        };  
        
        that.processDecoratorQueue = function () {
            processDecoratorQueue();
        };
        return that;
        
    };
    
    jQuery.extend(true, fluid.renderer, renderer);
  
    /*
     * This function is unsupported: It is not really intended for use by implementors.
     */
    fluid.ComponentReference = function (reference) {
        this.reference = reference;
    };
    
    // Explodes a raw "hash" into a list of UIOutput/UIBound entries
    fluid.explode = function (hash, basepath) {
        var togo = [];
        for (var key in hash) {
            var binding = basepath === undefined ? key : basepath + "." + key;
            togo[togo.length] = {ID: key, value: hash[key], valuebinding: binding};
        }
        return togo;
    };
      
    
   /**
    * A common utility function to make a simple view of rows, where each row has a selection control and a label
    * @param {Object} optionlist An array of the values of the options in the select
    * @param {Object} opts An object with this structure: {
            selectID: "",         
            rowID: "",            
            inputID: "",
            labelID: ""
        }
    */ 
    fluid.explodeSelectionToInputs = function (optionlist, opts) {
        return fluid.transform(optionlist, function (option, index) {
            return {
                ID: opts.rowID, 
                children: [
                    {ID: opts.inputID, parentRelativeID: "..::" + opts.selectID, choiceindex: index},
                    {ID: opts.labelID, parentRelativeID: "..::" + opts.selectID, choiceindex: index}]
            };
        });
    };
  
    fluid.resolveMessageSource = function (messageSource) {
        if (messageSource.type === "data") {
            if (messageSource.url === undefined) {
                return fluid.messageLocator(messageSource.messages, messageSource.resolveFunc);
            }
            else {
              // TODO: fetch via AJAX, and convert format if necessary
            }
        } // jslint:ok - empty block
        else if (messageSource.type === "resolver") {
            return messageSource.resolver.resolve;
        }
    };
    
    fluid.renderTemplates = function (templates, tree, options, fossilsIn) {
        var renderer = fluid.renderer(templates, tree, options, fossilsIn);
        var rendered = renderer.renderTemplates();
        return rendered;
    };
    /** A driver to render and bind an already parsed set of templates onto
     * a node. See documentation for fluid.selfRender.
     * @param templates A parsed template set, as returned from fluid.selfRender or 
     * fluid.parseTemplates.
     */
  
    fluid.reRender = function (templates, node, tree, options) {
        options = options || {};
        var renderer = fluid.renderer(templates, tree, options, options.fossils);
        options = renderer.options;
              // Empty the node first, to head off any potential id collisions when rendering
        node = fluid.unwrap(node);
        var lastFocusedElement = fluid.getLastFocusedElement ? fluid.getLastFocusedElement() : null;
        var lastId;
        if (lastFocusedElement && fluid.dom.isContainer(node, lastFocusedElement)) {
            lastId = lastFocusedElement.id;
        }
        if ($.browser.msie) {
            options.jQuery(node).empty(); //- this operation is very slow.
        }
        else {
            node.innerHTML = "";
        }
        
        var rendered = renderer.renderTemplates();
        if (options.renderRaw) {
            rendered = fluid.XMLEncode(rendered);
            rendered = rendered.replace(/\n/g, "<br/>");
        }
        if (options.model) {
            fluid.bindFossils(node, options.model, options.fossils);
        }
        if ($.browser.msie) {
            options.jQuery(node).html(rendered);
        }
        else {
            node.innerHTML = rendered;
        }
        renderer.processDecoratorQueue();
        if (lastId) {
            var element = fluid.byId(lastId, options.document);
            if (element) {
                options.jQuery(element).focus();
            }      
        }
          
        return templates;
    };
  
    function findNodeValue(rootNode) {
        var node = fluid.dom.iterateDom(rootNode, function (node) {
          // NB, in Firefox at least, comment and cdata nodes cannot be distinguished!
            return node.nodeType === 8 || node.nodeType === 4 ? "stop" : null;
            }, true); // jslint:ok
        var value = node.nodeValue;
        if (value.indexOf("[CDATA[") === 0) {
            return value.substring(6, value.length - 2);
        }
        else {
            return value;
        }
    }
  
    fluid.extractTemplate = function (node, armouring) {
        if (!armouring) {
            return node.innerHTML;
        }
        else {
            return findNodeValue(node);
        }
    };
    /** A slightly generalised version of fluid.selfRender that does not assume that the
     * markup used to source the template is within the target node.
     * @param source Either a structure {node: node, armouring: armourstyle} or a string
     * holding a literal template
     * @param target The node to receive the rendered markup
     * @param tree, options, return as for fluid.selfRender
     */
    fluid.render = function (source, target, tree, options) {
        options = options || {};
        var template = source;
        if (typeof(source) === "object") {
            template = fluid.extractTemplate(fluid.unwrap(source.node), source.armouring);
        }
        target = fluid.unwrap(target);
        var resourceSpec = {base: {resourceText: template, 
                            href: ".", resourceKey: ".", cutpoints: options.cutpoints}
                            };
        var templates = fluid.parseTemplates(resourceSpec, ["base"], options);
        return fluid.reRender(templates, target, tree, options);    
    };
    
    /** A simple driver for single node self-templating. Treats the markup for a
     * node as a template, parses it into a template structure, renders it using
     * the supplied component tree and options, then replaces the markup in the 
     * node with the rendered markup, and finally performs any required data
     * binding. The parsed template is returned for use with a further call to
     * reRender.
     * @param node The node both holding the template, and whose markup is to be
     * replaced with the rendered result.
     * @param tree The component tree to be rendered.
     * @param options An options structure to configure the rendering and binding process.
     * @return A templates structure, suitable for a further call to fluid.reRender or
     * fluid.renderTemplates.
     */  
    fluid.selfRender = function (node, tree, options) {
        options = options || {};
        return fluid.render({node: node, armouring: options.armouring}, node, tree, options);
    };

})(jQuery, fluid_1_5);
/*
Copyright 2008-2010 University of Cambridge
Copyright 2008-2009 University of Toronto
Copyright 2010-2011 Lucendo Development Ltd.

Licensed under the Educational Community License (ECL), Version 2.0 or the New
BSD license. You may not use this file except in compliance with one these
Licenses.

You may obtain a copy of the ECL 2.0 License and BSD License at
https://github.com/fluid-project/infusion/raw/master/Infusion-LICENSE.txt
*/

// Declare dependencies
/*global fluid_1_5:true, jQuery*/

// JSLint options 
/*jslint white: true, funcinvoke: true, continue: true, elsecatch: true, operator: true, jslintok:true, undef: true, newcap: true, regexp: true, bitwise: true, browser: true, forin: true, maxerr: 100, indent: 4 */

fluid_1_5 = fluid_1_5 || {};

(function ($, fluid) {

    if (!fluid.renderer) {
        fluid.fail("fluidRenderer.js is a necessary dependency of RendererUtilities");
    }
    
    /** Returns an array of size count, filled with increasing integers, 
     *  starting at 0 or at the index specified by first. 
     */
    
    fluid.iota = function (count, first) {
        first = first || 0;
        var togo = [];
        for (var i = 0; i < count; ++i) {
            togo[togo.length] = first++;
        }
        return togo;
    };
    
    fluid.renderer.visitDecorators = function(that, visitor) {
        fluid.visitComponentChildren(that, function(component, name) {
            if (name.indexOf(fluid.renderer.decoratorComponentPrefix) === 0) {
                visitor(component, name);
            }
        }, {flat: true});  
    };

    fluid.renderer.clearDecorators = function(instantiator, that) {
        fluid.renderer.visitDecorators(that, function(component, name) {
            instantiator.clearComponent(that, name);
        });
    };
    
    fluid.renderer.getDecoratorComponents = function(that) {
        var togo = {};
        fluid.renderer.visitDecorators(that, function(component, name) {
            togo[name] = component;
        });
        return togo;
    };

    // Utilities for coordinating options in renderer components - this code is all pretty
    // dreadful and needs to be organised as a suitable set of defaults and policies
    fluid.renderer.modeliseOptions = function (options, defaults, baseOptions) {
        return $.extend({}, defaults, options, fluid.filterKeys(baseOptions, ["model", "applier"]));
    };
    fluid.renderer.reverseMerge = function (target, source, names) {
        names = fluid.makeArray(names);
        fluid.each(names, function (name) {
            if (target[name] === undefined && source[name] !== undefined) {
                target[name] = source[name];
            }
        });
    };

    /** "Renderer component" infrastructure **/
  // TODO: fix this up with IoC and improved handling of templateSource as well as better 
  // options layout (model appears in both rOpts and eOpts)
    fluid.renderer.createRendererSubcomponent = function (container, selectors, options, baseObject, fossils) {
        options = options || {};
        var source = options.templateSource ? options.templateSource : {node: $(container)};
        var rendererOptions = fluid.renderer.modeliseOptions(options.rendererOptions, null, baseObject);
        rendererOptions.fossils = fossils || {};
        if (container.jquery) {
            var cascadeOptions = {
                document: container[0].ownerDocument,
                jQuery: container.constructor  
            };
            fluid.renderer.reverseMerge(rendererOptions, cascadeOptions, fluid.keys(cascadeOptions));
        }
        
        var expanderOptions = fluid.renderer.modeliseOptions(options.expanderOptions, {ELstyle: "${}"}, baseObject);
        fluid.renderer.reverseMerge(expanderOptions, options, ["resolverGetConfig", "resolverSetConfig"]);
        var that = {};
        if (!options.noexpand) {
            that.expander = fluid.renderer.makeProtoExpander(expanderOptions);
        }
        
        var templates = null;
        that.render = function (tree) {
            var cutpointFn = options.cutpointGenerator || "fluid.renderer.selectorsToCutpoints";
            rendererOptions.cutpoints = rendererOptions.cutpoints || fluid.invokeGlobalFunction(cutpointFn, [selectors, options]);
            container = typeof(container) === "function" ? container() : $(container);
              
            if (templates) {
                fluid.clear(rendererOptions.fossils);
                fluid.reRender(templates, container, tree, rendererOptions);
            } 
            else {
                if (typeof(source) === "function") { // TODO: make a better attempt than this at asynchrony
                    source = source();  
                }
                templates = fluid.render(source, container, tree, rendererOptions);
            }
        };
        return that;
    };
    
    fluid.defaults("fluid.rendererComponent", {
        gradeNames: ["fluid.viewComponent"],
        initFunction: "fluid.initRendererComponent",
        mergePolicy: {
            protoTree: "noexpand, replace",
            parentBundle: "nomerge"
        },
        rendererOptions: {
            autoBind: true
        },
        events: {
            prepareModelForRender: null,
            onRenderTree: null,
            afterRender: null,
            produceTree: "unicast"
        }
    });

    fluid.initRendererComponent = function (componentName, container, options) {
        var that = fluid.initView(componentName, container, options, {gradeNames: ["fluid.rendererComponent"]});
        
        fluid.fetchResources(that.options.resources); // TODO: deal with asynchrony
        
        var rendererOptions = fluid.renderer.modeliseOptions(that.options.rendererOptions, null, that);
        if (!that.options.noUpgradeDecorators) {
            fluid.withInstantiator(that, function(currentInst) {
                rendererOptions.instantiator = currentInst;
                rendererOptions.parentComponent = that;
            });
        }
        var messageResolver;
        if (!rendererOptions.messageSource && that.options.strings) {
            messageResolver = fluid.messageResolver({
                messageBase: that.options.strings,
                resolveFunc: that.options.messageResolverFunction,
                parents: fluid.makeArray(that.options.parentBundle)
            });
            rendererOptions.messageSource = {type: "resolver", resolver: messageResolver}; 
        }
        fluid.renderer.reverseMerge(rendererOptions, that.options, ["resolverGetConfig", "resolverSetConfig"]);


        var rendererFnOptions = $.extend({}, that.options.rendererFnOptions, { 
            rendererOptions: rendererOptions,
            repeatingSelectors: that.options.repeatingSelectors,
            selectorsToIgnore: that.options.selectorsToIgnore,
            expanderOptions: {
                envAdd: {styles: that.options.styles}
            }
        });
           
        if (that.options.resources && that.options.resources.template) {
            rendererFnOptions.templateSource = function () { // TODO: don't obliterate, multitemplates, etc.
                return that.options.resources.template.resourceText;
            };
        }
        var produceTree = that.events.produceTree;
        produceTree.addListener(function() {
            return that.options.protoTree;
        });
        
        if (that.options.produceTree) {
            produceTree.addListener(that.options.produceTree);
        }

        fluid.renderer.reverseMerge(rendererFnOptions, that.options, ["resolverGetConfig", "resolverSetConfig"]);
        if (rendererFnOptions.rendererTargetSelector) {
            container = function () {return that.dom.locate(rendererFnOptions.rendererTargetSelector); };
        }
       
        var renderer = {
            fossils: {},
            boundPathForNode: function (node) {
                return fluid.boundPathForNode(node, renderer.fossils);
            }
        };
       
        var rendererSub = fluid.renderer.createRendererSubcomponent(container, that.options.selectors, rendererFnOptions, that, renderer.fossils);
        that.renderer = $.extend(renderer, rendererSub);
        
        if (messageResolver) {
            that.messageResolver = messageResolver;
        }

        that.refreshView = renderer.refreshView = function () {
            if (rendererOptions.instantiator && rendererOptions.parentComponent) {
                fluid.renderer.clearDecorators(rendererOptions.instantiator, rendererOptions.parentComponent);
            }
            that.events.prepareModelForRender.fire(that.model, that.applier, that);
            var tree = produceTree.fire(that);
            if (that.renderer.expander) {
                tree = that.renderer.expander(tree);
            }
            that.events.onRenderTree.fire(that, tree);
            that.renderer.render(tree);
            that.events.afterRender.fire(that);
        };
        
        if (that.options.renderOnInit) {
            that.refreshView();
        }
        
        return that;
    };
    
    var removeSelectors = function (selectors, selectorsToIgnore) {
        fluid.each(fluid.makeArray(selectorsToIgnore), function (selectorToIgnore) {
            delete selectors[selectorToIgnore];
        });
        return selectors;
    };

    var markRepeated = function (selectorKey, repeatingSelectors) {
        if (repeatingSelectors) {
            fluid.each(repeatingSelectors, function (repeatingSelector) {
                if (selectorKey === repeatingSelector) {
                    selectorKey = selectorKey + ":";
                }
            });
        }
        return selectorKey;
    };

    fluid.renderer.selectorsToCutpoints = function (selectors, options) {
        var togo = [];
        options = options || {};
        selectors = fluid.copy(selectors); // Make a copy before potentially destructively changing someone's selectors.
    
        if (options.selectorsToIgnore) {
            selectors = removeSelectors(selectors, options.selectorsToIgnore);
        }
    
        for (var selectorKey in selectors) {
            togo.push({
                id: markRepeated(selectorKey, options.repeatingSelectors),
                selector: selectors[selectorKey]
            });
        }
    
        return togo;
    };
  
    /** END of "Renderer Components" infrastructure **/
    
    fluid.renderer.NO_COMPONENT = {};
  
    /** A special "shallow copy" operation suitable for nondestructively
     * merging trees of components. jQuery.extend in shallow mode will 
     * neglect null valued properties.
     * This function is unsupported: It is not really intended for use by implementors.
     */
    fluid.renderer.mergeComponents = function (target, source) {
        for (var key in source) {
            target[key] = source[key];
        }
        return target;
    };
    
    fluid.registerNamespace("fluid.renderer.selection");
        
    /** Definition of expanders - firstly, "heavy" expanders **/
    
    fluid.renderer.selection.inputs = function (options, container, key, config) {
        fluid.expect("Selection to inputs expander", ["selectID", "inputID", "labelID", "rowID"], options);
        var selection = config.expander(options.tree);
        var rows = fluid.transform(selection.optionlist.value, function (option, index) {
            var togo = {};
            var element =  {parentRelativeID: "..::" + options.selectID, choiceindex: index};
            togo[options.inputID] = element;
            togo[options.labelID] = fluid.copy(element); 
            return togo;
        });
        var togo = {}; // TODO: JICO needs to support "quoted literal key initialisers" :P
        togo[options.selectID] = selection;
        togo[options.rowID] = {children: rows};
        togo = config.expander(togo);
        return togo;
    };
    
    fluid.renderer.repeat = function (options, container, key, config) {
        fluid.expect("Repetition expander", ["controlledBy", "tree"], options);
        var env = config.threadLocal();
        var path = fluid.extractContextualPath(options.controlledBy, {ELstyle: "ALL"}, env);
        var list = fluid.get(config.model, path, config.resolverGetConfig);
        
        var togo = {};
        if (!list || list.length === 0) {
            return options.ifEmpty ? config.expander(options.ifEmpty) : togo;
        }
        var expanded = [];
        fluid.each(list, function (element, i) {
            var EL = fluid.model.composePath(path, i);
            var envAdd = {}; 
            if (options.pathAs) {
                envAdd[options.pathAs] = "${" + EL + "}";
            }
            if (options.valueAs) {
                envAdd[options.valueAs] = fluid.get(config.model, EL, config.resolverGetConfig);
            }
            var expandrow = fluid.withEnvironment(envAdd, function() {
                return config.expander(options.tree);
            }, env);
            if (fluid.isArrayable(expandrow)) {
                if (expandrow.length > 0) {
                    expanded.push({children: expandrow});
                }
            }
            else if (expandrow !== fluid.renderer.NO_COMPONENT) {
                expanded.push(expandrow);
            }
        });
        var repeatID = options.repeatID;
        if (repeatID.indexOf(":") === -1) {
            repeatID = repeatID + ":";
        }
        fluid.each(expanded, function (entry) {entry.ID = repeatID; });
        return expanded;
    };
    
    fluid.renderer.condition = function (options, container, key, config) {
        fluid.expect("Selection to condition expander", ["condition"], options);
        var condition;
        if (options.condition.funcName) {
            var args = config.expandLight(options.condition.args);
            condition = fluid.invoke(options.condition.funcName, args);
        } else if (options.condition.expander) {
            condition = config.expander(options.condition);
        } else {
            condition = config.expandLight(options.condition);
        }
        var tree = (condition ? options.trueTree : options.falseTree);
        if (!tree) {
            tree = fluid.renderer.NO_COMPONENT;
        }
        return config.expander(tree);
    };
    
    
    /* An EL extraction utility suitable for context expressions which occur in 
     * expanding component trees. It assumes that any context expressions refer
     * to EL paths that are to be referred to the "true (direct) model" - since
     * the context during expansion may not agree with the context during rendering.
     * It satisfies the same contract as fluid.extractEL, in that it will either return
     * an EL path, or undefined if the string value supplied cannot be interpreted
     * as an EL path with respect to the supplied options.
     */
    // unsupported, non-API function
    fluid.extractContextualPath = function (string, options, env) {
        var parsed = fluid.extractELWithContext(string, options);
        if (parsed) {
            if (parsed.context) {
                return fluid.transformContextPath(parsed, env).path;
            }
            else {
                return parsed.path;
            }
        }
    };
    
    fluid.transformContextPath = function (parsed, env) {
        if (parsed.context) {
            var fetched = env[parsed.context];
            var EL;
            if (typeof(fetched) === "string") {
                EL = fluid.extractEL(fetched, {ELstyle: "${}"});
            }
            if (EL) {
                return {
                    noDereference: parsed.path === "", 
                    path: fluid.model.composePath(EL, parsed.path) 
                }; 
            }
        }
        return parsed;
    };

    /** Create a "protoComponent expander" with the supplied set of options.
     * The returned value will be a function which accepts a "protoComponent tree"
     * as argument, and returns a "fully expanded" tree suitable for supplying
     * directly to the renderer.
     * A "protoComponent tree" is similar to the "dehydrated form" accepted by
     * the historical renderer - only
     * i) The input format is unambiguous - this expander will NOT accept hydrated
     * components in the {ID: "myId, myfield: "myvalue"} form - but ONLY in
     * the dehydrated {myID: {myfield: myvalue}} form.
     * ii) This expander has considerably greater power to expand condensed trees.
     * In particular, an "EL style" option can be supplied which will expand bare
     * strings found as values in the tree into UIBound components by a configurable
     * strategy. Supported values for "ELstyle" are a) "ALL" - every string will be
     * interpreted as an EL reference and assigned to the "valuebinding" member of
     * the UIBound, or b) any single character, which if it appears as the first
     * character of the string, will mark it out as an EL reference - otherwise it
     * will be considered a literal value, or c) the value "${}" which will be
     * recognised bracketing any other EL expression.
     */

    fluid.renderer.makeProtoExpander = function (expandOptions) {
      // shallow copy of options - cheaply avoid destroying model, and all others are primitive
        var options = $.extend({
            ELstyle: "${}"
        }, expandOptions); // shallow copy of options
        var threadLocal; // rebound on every expansion at entry point
        
        function fetchEL(string) {
            var env = threadLocal();
            return fluid.extractContextualPath(string, options, env);
        }
         
        var IDescape = options.IDescape || "\\";
        
        var expandLight = function (source) {
            return fluid.resolveEnvironment(source, options); 
        };

        var expandBound = function (value, concrete) {
            if (value.messagekey !== undefined) {
                return {
                    componentType: "UIMessage",
                    messagekey: expandBound(value.messagekey),
                    args: expandLight(value.args)
                };
            }
            var proto;
            if (!fluid.isPrimitive(value) && !fluid.isArrayable(value)) {
                proto = $.extend({}, value);
                if (proto.decorators) {
                    proto.decorators = expandLight(proto.decorators);
                }
                value = proto.value;
                delete proto.value;
            } else {
                proto = {};
            }
            var EL = typeof (value) === "string" ? fetchEL(value) : null;
            if (EL) {
                proto.valuebinding = EL;
            } else if (value !== undefined) {
                proto.value = value;
            }
            if (options.model && proto.valuebinding && proto.value === undefined) {
                proto.value = fluid.get(options.model, proto.valuebinding, options.resolverGetConfig);
            }
            if (concrete) {
                proto.componentType = "UIBound";
            }
            return proto;
        };
        
        options.filter = fluid.expander.lightFilter;
        
        var expandCond;
        var expandLeafOrCond;
        
        var expandEntry = function (entry) {
            var comp = [];
            expandCond(entry, comp);
            return {children: comp};
        };
        
        var expandExternal = function (entry) {
            if (entry === fluid.renderer.NO_COMPONENT) {
                return entry;
            }
            var singleTarget;
            var target = [];
            var pusher = function (comp) {
                singleTarget = comp;
            };
            expandLeafOrCond(entry, target, pusher);
            return singleTarget || target;
        };
        
        var expandConfig = {
            model: options.model,
            resolverGetConfig: options.resolverGetConfig,
            resolverSetConfig: options.resolverSetConfig,
            expander: expandExternal,
            expandLight: expandLight
            //threadLocal: threadLocal
        };
        
        var expandLeaf = function (leaf, componentType) {
            var togo = {componentType: componentType};
            var map = fluid.renderer.boundMap[componentType] || {};
            for (var key in leaf) {
                if (/decorators|args/.test(key)) {
                    togo[key] = expandLight(leaf[key]);
                    continue;
                } else if (map[key]) {
                    togo[key] = expandBound(leaf[key]);
                } else {
                    togo[key] = leaf[key];
                }
            }
            return togo;
        };
        
        // A child entry may be a cond, a leaf, or another "thing with children".
        // Unlike the case with a cond's contents, these must be homogeneous - at least
        // they may either be ALL leaves, or else ALL cond/childed etc. 
        // In all of these cases, the key will be THE PARENT'S KEY
        var expandChildren = function (entry, pusher) {
            var children = entry.children;
            for (var i = 0; i < children.length; ++i) {
                // each child in this list will lead to a WHOLE FORKED set of children.
                var target = [];
                var comp = { children: target};
                var child = children[i];
                var childPusher = function (comp) {
                    target[target.length] = comp;
                }; // jslint:ok - function in loop 
                expandLeafOrCond(child, target, childPusher);
                // Rescue the case of an expanded leaf into single component - TODO: check what sense this makes of the grammar
                if (comp.children.length === 1 && !comp.children[0].ID) {
                    comp = comp.children[0];
                }
                pusher(comp); 
            }
        };
        
        function detectBareBound(entry) {
            return fluid.find(entry, function (value, key) {
                return key === "decorators";
            }) !== false;
        }
        
        // We have reached something which is either a leaf or Cond - either inside
        // a Cond or as an entry in children.
        var expandLeafOrCond = function (entry, target, pusher) { // jslint:ok - forward declaration
            var componentType = fluid.renderer.inferComponentType(entry);
            if (!componentType && (fluid.isPrimitive(entry) || detectBareBound(entry))) {
                componentType = "UIBound";
            }
            if (componentType) {
                pusher(componentType === "UIBound" ? expandBound(entry, true) : expandLeaf(entry, componentType));
            } else {
              // we couldn't recognise it as a leaf, so it must be a cond
              // this may be illegal if we are already in a cond.
                if (!target) {
                    fluid.fail("Illegal cond->cond transition");
                }
                expandCond(entry, target);
            }
        };
        
        // cond entry may be a leaf, "thing with children" or a "direct bound".
        // a Cond can ONLY occur as a direct member of "children". Each "cond" entry may
        // give rise to one or many elements with the SAME key - if "expandSingle" discovers
        // "thing with children" they will all share the same key found in proto. 
        expandCond = function (proto, target) {
            for (var key in proto) {
                var entry = proto[key];
                if (key.charAt(0) === IDescape) {
                    key = key.substring(1);
                }
                if (key === "expander") {
                    var expanders = fluid.makeArray(entry);
                    fluid.each(expanders, function (expander) {
                        var expanded = fluid.invokeGlobalFunction(expander.type, [expander, proto, key, expandConfig]);
                        if (expanded !== fluid.renderer.NO_COMPONENT) {
                            fluid.each(expanded, function (el) {target[target.length] = el; });
                        }
                    }); // jslint:ok - function in loop
                } else if (entry) {
                    var condPusher = function (comp) {
                        comp.ID = key;
                        target[target.length] = comp; 
                    }; // jslint:ok - function in loop

                    if (entry.children) {
                        if (key.indexOf(":") === -1) {
                            key = key + ":";
                        }
                        expandChildren(entry, condPusher);
                    } else if (fluid.renderer.isBoundPrimitive(entry)) {
                        condPusher(expandBound(entry, true));
                    } else {
                        expandLeafOrCond(entry, null, condPusher);
                    }
                }
            }
                
        };
        
        return function(entry) {
            threadLocal = fluid.threadLocal(function() {
                return $.extend({}, options.envAdd);
            });
            options.fetcher = fluid.makeEnvironmentFetcher(options.model, fluid.transformContextPath, threadLocal);
            expandConfig.threadLocal = threadLocal;
            return expandEntry(entry);
        };
    };
    
})(jQuery, fluid_1_5);
    /*
 * jQuery UI Draggable 1.8.12
 *
 * Copyright 2011, AUTHORS.txt (http://jqueryui.com/about)
 * Dual licensed under the MIT or GPL Version 2 licenses.
 * http://jquery.org/license
 *
 * http://docs.jquery.com/UI/Draggables
 *
 * Depends:
 *	jquery.ui.core.js
 *	jquery.ui.mouse.js
 *	jquery.ui.widget.js
 */
(function( $, undefined ) {

$.widget("ui.draggable", $.ui.mouse, {
	widgetEventPrefix: "drag",
	options: {
		addClasses: true,
		appendTo: "parent",
		axis: false,
		connectToSortable: false,
		containment: false,
		cursor: "auto",
		cursorAt: false,
		grid: false,
		handle: false,
		helper: "original",
		iframeFix: false,
		opacity: false,
		refreshPositions: false,
		revert: false,
		revertDuration: 500,
		scope: "default",
		scroll: true,
		scrollSensitivity: 20,
		scrollSpeed: 20,
		snap: false,
		snapMode: "both",
		snapTolerance: 20,
		stack: false,
		zIndex: false
	},
	_create: function() {

		if (this.options.helper == 'original' && !(/^(?:r|a|f)/).test(this.element.css("position")))
			this.element[0].style.position = 'relative';

		(this.options.addClasses && this.element.addClass("ui-draggable"));
		(this.options.disabled && this.element.addClass("ui-draggable-disabled"));

		this._mouseInit();

	},

	destroy: function() {
		if(!this.element.data('draggable')) return;
		this.element
			.removeData("draggable")
			.unbind(".draggable")
			.removeClass("ui-draggable"
				+ " ui-draggable-dragging"
				+ " ui-draggable-disabled");
		this._mouseDestroy();

		return this;
	},

	_mouseCapture: function(event) {

		var o = this.options;

		// among others, prevent a drag on a resizable-handle
		if (this.helper || o.disabled || $(event.target).is('.ui-resizable-handle'))
			return false;

		//Quit if we're not on a valid handle
		this.handle = this._getHandle(event);
		if (!this.handle)
			return false;

		return true;

	},

	_mouseStart: function(event) {

		var o = this.options;

		//Create and append the visible helper
		this.helper = this._createHelper(event);

		//Cache the helper size
		this._cacheHelperProportions();

		//If ddmanager is used for droppables, set the global draggable
		if($.ui.ddmanager)
			$.ui.ddmanager.current = this;

		/*
		 * - Position generation -
		 * This block generates everything position related - it's the core of draggables.
		 */

		//Cache the margins of the original element
		this._cacheMargins();

		//Store the helper's css position
		this.cssPosition = this.helper.css("position");
		this.scrollParent = this.helper.scrollParent();

		//The element's absolute position on the page minus margins
		this.offset = this.positionAbs = this.element.offset();
		this.offset = {
			top: this.offset.top - this.margins.top,
			left: this.offset.left - this.margins.left
		};

		$.extend(this.offset, {
			click: { //Where the click happened, relative to the element
				left: event.pageX - this.offset.left,
				top: event.pageY - this.offset.top
			},
			parent: this._getParentOffset(),
			relative: this._getRelativeOffset() //This is a relative to absolute position minus the actual position calculation - only used for relative positioned helper
		});

		//Generate the original position
		this.originalPosition = this.position = this._generatePosition(event);
		this.originalPageX = event.pageX;
		this.originalPageY = event.pageY;

		//Adjust the mouse offset relative to the helper if 'cursorAt' is supplied
		(o.cursorAt && this._adjustOffsetFromHelper(o.cursorAt));

		//Set a containment if given in the options
		if(o.containment)
			this._setContainment();

		//Trigger event + callbacks
		if(this._trigger("start", event) === false) {
			this._clear();
			return false;
		}

		//Recache the helper size
		this._cacheHelperProportions();

		//Prepare the droppable offsets
		if ($.ui.ddmanager && !o.dropBehaviour)
			$.ui.ddmanager.prepareOffsets(this, event);

		this.helper.addClass("ui-draggable-dragging");
		this._mouseDrag(event, true); //Execute the drag once - this causes the helper not to be visible before getting its correct position
		return true;
	},

	_mouseDrag: function(event, noPropagation) {

		//Compute the helpers position
		this.position = this._generatePosition(event);
		this.positionAbs = this._convertPositionTo("absolute");

		//Call plugins and callbacks and use the resulting position if something is returned
		if (!noPropagation) {
			var ui = this._uiHash();
			if(this._trigger('drag', event, ui) === false) {
				this._mouseUp({});
				return false;
			}
			this.position = ui.position;
		}

		if(!this.options.axis || this.options.axis != "y") this.helper[0].style.left = this.position.left+'px';
		if(!this.options.axis || this.options.axis != "x") this.helper[0].style.top = this.position.top+'px';
		if($.ui.ddmanager) $.ui.ddmanager.drag(this, event);

		return false;
	},

	_mouseStop: function(event) {

		//If we are using droppables, inform the manager about the drop
		var dropped = false;
		if ($.ui.ddmanager && !this.options.dropBehaviour)
			dropped = $.ui.ddmanager.drop(this, event);

		//if a drop comes from outside (a sortable)
		if(this.dropped) {
			dropped = this.dropped;
			this.dropped = false;
		}
		
		//if the original element is removed, don't bother to continue if helper is set to "original"
		if((!this.element[0] || !this.element[0].parentNode) && this.options.helper == "original")
			return false;

		if((this.options.revert == "invalid" && !dropped) || (this.options.revert == "valid" && dropped) || this.options.revert === true || ($.isFunction(this.options.revert) && this.options.revert.call(this.element, dropped))) {
			var self = this;
			$(this.helper).animate(this.originalPosition, parseInt(this.options.revertDuration, 10), function() {
				if(self._trigger("stop", event) !== false) {
					self._clear();
				}
			});
		} else {
			if(this._trigger("stop", event) !== false) {
				this._clear();
			}
		}

		return false;
	},
	
	cancel: function() {
		
		if(this.helper.is(".ui-draggable-dragging")) {
			this._mouseUp({});
		} else {
			this._clear();
		}
		
		return this;
		
	},

	_getHandle: function(event) {

		var handle = !this.options.handle || !$(this.options.handle, this.element).length ? true : false;
		$(this.options.handle, this.element)
			.find("*")
			.andSelf()
			.each(function() {
				if(this == event.target) handle = true;
			});

		return handle;

	},

	_createHelper: function(event) {

		var o = this.options;
		var helper = $.isFunction(o.helper) ? $(o.helper.apply(this.element[0], [event])) : (o.helper == 'clone' ? this.element.clone() : this.element);

		if(!helper.parents('body').length)
			helper.appendTo((o.appendTo == 'parent' ? this.element[0].parentNode : o.appendTo));

		if(helper[0] != this.element[0] && !(/(fixed|absolute)/).test(helper.css("position")))
			helper.css("position", "absolute");

		return helper;

	},

	_adjustOffsetFromHelper: function(obj) {
		if (typeof obj == 'string') {
			obj = obj.split(' ');
		}
		if ($.isArray(obj)) {
			obj = {left: +obj[0], top: +obj[1] || 0};
		}
		if ('left' in obj) {
			this.offset.click.left = obj.left + this.margins.left;
		}
		if ('right' in obj) {
			this.offset.click.left = this.helperProportions.width - obj.right + this.margins.left;
		}
		if ('top' in obj) {
			this.offset.click.top = obj.top + this.margins.top;
		}
		if ('bottom' in obj) {
			this.offset.click.top = this.helperProportions.height - obj.bottom + this.margins.top;
		}
	},

	_getParentOffset: function() {

		//Get the offsetParent and cache its position
		this.offsetParent = this.helper.offsetParent();
		var po = this.offsetParent.offset();

		// This is a special case where we need to modify a offset calculated on start, since the following happened:
		// 1. The position of the helper is absolute, so it's position is calculated based on the next positioned parent
		// 2. The actual offset parent is a child of the scroll parent, and the scroll parent isn't the document, which means that
		//    the scroll is included in the initial calculation of the offset of the parent, and never recalculated upon drag
		if(this.cssPosition == 'absolute' && this.scrollParent[0] != document && $.ui.contains(this.scrollParent[0], this.offsetParent[0])) {
			po.left += this.scrollParent.scrollLeft();
			po.top += this.scrollParent.scrollTop();
		}

		if((this.offsetParent[0] == document.body) //This needs to be actually done for all browsers, since pageX/pageY includes this information
		|| (this.offsetParent[0].tagName && this.offsetParent[0].tagName.toLowerCase() == 'html' && $.browser.msie)) //Ugly IE fix
			po = { top: 0, left: 0 };

		return {
			top: po.top + (parseInt(this.offsetParent.css("borderTopWidth"),10) || 0),
			left: po.left + (parseInt(this.offsetParent.css("borderLeftWidth"),10) || 0)
		};

	},

	_getRelativeOffset: function() {

		if(this.cssPosition == "relative") {
			var p = this.element.position();
			return {
				top: p.top - (parseInt(this.helper.css("top"),10) || 0) + this.scrollParent.scrollTop(),
				left: p.left - (parseInt(this.helper.css("left"),10) || 0) + this.scrollParent.scrollLeft()
			};
		} else {
			return { top: 0, left: 0 };
		}

	},

	_cacheMargins: function() {
		this.margins = {
			left: (parseInt(this.element.css("marginLeft"),10) || 0),
			top: (parseInt(this.element.css("marginTop"),10) || 0),
			right: (parseInt(this.element.css("marginRight"),10) || 0),
			bottom: (parseInt(this.element.css("marginBottom"),10) || 0)
		};
	},

	_cacheHelperProportions: function() {
		this.helperProportions = {
			width: this.helper.outerWidth(),
			height: this.helper.outerHeight()
		};
	},

	_setContainment: function() {

		var o = this.options;
		if(o.containment == 'parent') o.containment = this.helper[0].parentNode;
		if(o.containment == 'document' || o.containment == 'window') this.containment = [
			(o.containment == 'document' ? 0 : $(window).scrollLeft()) - this.offset.relative.left - this.offset.parent.left,
			(o.containment == 'document' ? 0 : $(window).scrollTop()) - this.offset.relative.top - this.offset.parent.top,
			(o.containment == 'document' ? 0 : $(window).scrollLeft()) + $(o.containment == 'document' ? document : window).width() - this.helperProportions.width - this.margins.left,
			(o.containment == 'document' ? 0 : $(window).scrollTop()) + ($(o.containment == 'document' ? document : window).height() || document.body.parentNode.scrollHeight) - this.helperProportions.height - this.margins.top
		];

		if(!(/^(document|window|parent)$/).test(o.containment) && o.containment.constructor != Array) {
			var ce = $(o.containment)[0]; if(!ce) return;
			var co = $(o.containment).offset();
			var over = ($(ce).css("overflow") != 'hidden');

			this.containment = [
				co.left + (parseInt($(ce).css("borderLeftWidth"),10) || 0) + (parseInt($(ce).css("paddingLeft"),10) || 0),
				co.top + (parseInt($(ce).css("borderTopWidth"),10) || 0) + (parseInt($(ce).css("paddingTop"),10) || 0),
				co.left+(over ? Math.max(ce.scrollWidth,ce.offsetWidth) : ce.offsetWidth) - (parseInt($(ce).css("borderLeftWidth"),10) || 0) - (parseInt($(ce).css("paddingRight"),10) || 0) - this.helperProportions.width - this.margins.left - this.margins.right,
				co.top+(over ? Math.max(ce.scrollHeight,ce.offsetHeight) : ce.offsetHeight) - (parseInt($(ce).css("borderTopWidth"),10) || 0) - (parseInt($(ce).css("paddingBottom"),10) || 0) - this.helperProportions.height - this.margins.top  - this.margins.bottom
			];
		} else if(o.containment.constructor == Array) {
			this.containment = o.containment;
		}

	},

	_convertPositionTo: function(d, pos) {

		if(!pos) pos = this.position;
		var mod = d == "absolute" ? 1 : -1;
		var o = this.options, scroll = this.cssPosition == 'absolute' && !(this.scrollParent[0] != document && $.ui.contains(this.scrollParent[0], this.offsetParent[0])) ? this.offsetParent : this.scrollParent, scrollIsRootNode = (/(html|body)/i).test(scroll[0].tagName);

		return {
			top: (
				pos.top																	// The absolute mouse position
				+ this.offset.relative.top * mod										// Only for relative positioned nodes: Relative offset from element to offset parent
				+ this.offset.parent.top * mod											// The offsetParent's offset without borders (offset + border)
				- ($.browser.safari && $.browser.version < 526 && this.cssPosition == 'fixed' ? 0 : ( this.cssPosition == 'fixed' ? -this.scrollParent.scrollTop() : ( scrollIsRootNode ? 0 : scroll.scrollTop() ) ) * mod)
			),
			left: (
				pos.left																// The absolute mouse position
				+ this.offset.relative.left * mod										// Only for relative positioned nodes: Relative offset from element to offset parent
				+ this.offset.parent.left * mod											// The offsetParent's offset without borders (offset + border)
				- ($.browser.safari && $.browser.version < 526 && this.cssPosition == 'fixed' ? 0 : ( this.cssPosition == 'fixed' ? -this.scrollParent.scrollLeft() : scrollIsRootNode ? 0 : scroll.scrollLeft() ) * mod)
			)
		};

	},

	_generatePosition: function(event) {

		var o = this.options, scroll = this.cssPosition == 'absolute' && !(this.scrollParent[0] != document && $.ui.contains(this.scrollParent[0], this.offsetParent[0])) ? this.offsetParent : this.scrollParent, scrollIsRootNode = (/(html|body)/i).test(scroll[0].tagName);
		var pageX = event.pageX;
		var pageY = event.pageY;

		/*
		 * - Position constraining -
		 * Constrain the position to a mix of grid, containment.
		 */

		if(this.originalPosition) { //If we are not dragging yet, we won't check for options

			if(this.containment) {
				if(event.pageX - this.offset.click.left < this.containment[0]) pageX = this.containment[0] + this.offset.click.left;
				if(event.pageY - this.offset.click.top < this.containment[1]) pageY = this.containment[1] + this.offset.click.top;
				if(event.pageX - this.offset.click.left > this.containment[2]) pageX = this.containment[2] + this.offset.click.left;
				if(event.pageY - this.offset.click.top > this.containment[3]) pageY = this.containment[3] + this.offset.click.top;
			}

			if(o.grid) {
				var top = this.originalPageY + Math.round((pageY - this.originalPageY) / o.grid[1]) * o.grid[1];
				pageY = this.containment ? (!(top - this.offset.click.top < this.containment[1] || top - this.offset.click.top > this.containment[3]) ? top : (!(top - this.offset.click.top < this.containment[1]) ? top - o.grid[1] : top + o.grid[1])) : top;

				var left = this.originalPageX + Math.round((pageX - this.originalPageX) / o.grid[0]) * o.grid[0];
				pageX = this.containment ? (!(left - this.offset.click.left < this.containment[0] || left - this.offset.click.left > this.containment[2]) ? left : (!(left - this.offset.click.left < this.containment[0]) ? left - o.grid[0] : left + o.grid[0])) : left;
			}

		}

		return {
			top: (
				pageY																// The absolute mouse position
				- this.offset.click.top													// Click offset (relative to the element)
				- this.offset.relative.top												// Only for relative positioned nodes: Relative offset from element to offset parent
				- this.offset.parent.top												// The offsetParent's offset without borders (offset + border)
				+ ($.browser.safari && $.browser.version < 526 && this.cssPosition == 'fixed' ? 0 : ( this.cssPosition == 'fixed' ? -this.scrollParent.scrollTop() : ( scrollIsRootNode ? 0 : scroll.scrollTop() ) ))
			),
			left: (
				pageX																// The absolute mouse position
				- this.offset.click.left												// Click offset (relative to the element)
				- this.offset.relative.left												// Only for relative positioned nodes: Relative offset from element to offset parent
				- this.offset.parent.left												// The offsetParent's offset without borders (offset + border)
				+ ($.browser.safari && $.browser.version < 526 && this.cssPosition == 'fixed' ? 0 : ( this.cssPosition == 'fixed' ? -this.scrollParent.scrollLeft() : scrollIsRootNode ? 0 : scroll.scrollLeft() ))
			)
		};

	},

	_clear: function() {
		this.helper.removeClass("ui-draggable-dragging");
		if(this.helper[0] != this.element[0] && !this.cancelHelperRemoval) this.helper.remove();
		//if($.ui.ddmanager) $.ui.ddmanager.current = null;
		this.helper = null;
		this.cancelHelperRemoval = false;
	},

	// From now on bulk stuff - mainly helpers

	_trigger: function(type, event, ui) {
		ui = ui || this._uiHash();
		$.ui.plugin.call(this, type, [event, ui]);
		if(type == "drag") this.positionAbs = this._convertPositionTo("absolute"); //The absolute position has to be recalculated after plugins
		return $.Widget.prototype._trigger.call(this, type, event, ui);
	},

	plugins: {},

	_uiHash: function(event) {
		return {
			helper: this.helper,
			position: this.position,
			originalPosition: this.originalPosition,
			offset: this.positionAbs
		};
	}

});

$.extend($.ui.draggable, {
	version: "1.8.12"
});

$.ui.plugin.add("draggable", "connectToSortable", {
	start: function(event, ui) {

		var inst = $(this).data("draggable"), o = inst.options,
			uiSortable = $.extend({}, ui, { item: inst.element });
		inst.sortables = [];
		$(o.connectToSortable).each(function() {
			var sortable = $.data(this, 'sortable');
			if (sortable && !sortable.options.disabled) {
				inst.sortables.push({
					instance: sortable,
					shouldRevert: sortable.options.revert
				});
				sortable.refreshPositions();	// Call the sortable's refreshPositions at drag start to refresh the containerCache since the sortable container cache is used in drag and needs to be up to date (this will ensure it's initialised as well as being kept in step with any changes that might have happened on the page).
				sortable._trigger("activate", event, uiSortable);
			}
		});

	},
	stop: function(event, ui) {

		//If we are still over the sortable, we fake the stop event of the sortable, but also remove helper
		var inst = $(this).data("draggable"),
			uiSortable = $.extend({}, ui, { item: inst.element });

		$.each(inst.sortables, function() {
			if(this.instance.isOver) {

				this.instance.isOver = 0;

				inst.cancelHelperRemoval = true; //Don't remove the helper in the draggable instance
				this.instance.cancelHelperRemoval = false; //Remove it in the sortable instance (so sortable plugins like revert still work)

				//The sortable revert is supported, and we have to set a temporary dropped variable on the draggable to support revert: 'valid/invalid'
				if(this.shouldRevert) this.instance.options.revert = true;

				//Trigger the stop of the sortable
				this.instance._mouseStop(event);

				this.instance.options.helper = this.instance.options._helper;

				//If the helper has been the original item, restore properties in the sortable
				if(inst.options.helper == 'original')
					this.instance.currentItem.css({ top: 'auto', left: 'auto' });

			} else {
				this.instance.cancelHelperRemoval = false; //Remove the helper in the sortable instance
				this.instance._trigger("deactivate", event, uiSortable);
			}

		});

	},
	drag: function(event, ui) {

		var inst = $(this).data("draggable"), self = this;

		var checkPos = function(o) {
			var dyClick = this.offset.click.top, dxClick = this.offset.click.left;
			var helperTop = this.positionAbs.top, helperLeft = this.positionAbs.left;
			var itemHeight = o.height, itemWidth = o.width;
			var itemTop = o.top, itemLeft = o.left;

			return $.ui.isOver(helperTop + dyClick, helperLeft + dxClick, itemTop, itemLeft, itemHeight, itemWidth);
		};

		$.each(inst.sortables, function(i) {
			
			//Copy over some variables to allow calling the sortable's native _intersectsWith
			this.instance.positionAbs = inst.positionAbs;
			this.instance.helperProportions = inst.helperProportions;
			this.instance.offset.click = inst.offset.click;
			
			if(this.instance._intersectsWith(this.instance.containerCache)) {

				//If it intersects, we use a little isOver variable and set it once, so our move-in stuff gets fired only once
				if(!this.instance.isOver) {

					this.instance.isOver = 1;
					//Now we fake the start of dragging for the sortable instance,
					//by cloning the list group item, appending it to the sortable and using it as inst.currentItem
					//We can then fire the start event of the sortable with our passed browser event, and our own helper (so it doesn't create a new one)
					this.instance.currentItem = $(self).clone().appendTo(this.instance.element).data("sortable-item", true);
					this.instance.options._helper = this.instance.options.helper; //Store helper option to later restore it
					this.instance.options.helper = function() { return ui.helper[0]; };

					event.target = this.instance.currentItem[0];
					this.instance._mouseCapture(event, true);
					this.instance._mouseStart(event, true, true);

					//Because the browser event is way off the new appended portlet, we modify a couple of variables to reflect the changes
					this.instance.offset.click.top = inst.offset.click.top;
					this.instance.offset.click.left = inst.offset.click.left;
					this.instance.offset.parent.left -= inst.offset.parent.left - this.instance.offset.parent.left;
					this.instance.offset.parent.top -= inst.offset.parent.top - this.instance.offset.parent.top;

					inst._trigger("toSortable", event);
					inst.dropped = this.instance.element; //draggable revert needs that
					//hack so receive/update callbacks work (mostly)
					inst.currentItem = inst.element;
					this.instance.fromOutside = inst;

				}

				//Provided we did all the previous steps, we can fire the drag event of the sortable on every draggable drag, when it intersects with the sortable
				if(this.instance.currentItem) this.instance._mouseDrag(event);

			} else {

				//If it doesn't intersect with the sortable, and it intersected before,
				//we fake the drag stop of the sortable, but make sure it doesn't remove the helper by using cancelHelperRemoval
				if(this.instance.isOver) {

					this.instance.isOver = 0;
					this.instance.cancelHelperRemoval = true;
					
					//Prevent reverting on this forced stop
					this.instance.options.revert = false;
					
					// The out event needs to be triggered independently
					this.instance._trigger('out', event, this.instance._uiHash(this.instance));
					
					this.instance._mouseStop(event, true);
					this.instance.options.helper = this.instance.options._helper;

					//Now we remove our currentItem, the list group clone again, and the placeholder, and animate the helper back to it's original size
					this.instance.currentItem.remove();
					if(this.instance.placeholder) this.instance.placeholder.remove();

					inst._trigger("fromSortable", event);
					inst.dropped = false; //draggable revert needs that
				}

			};

		});

	}
});

$.ui.plugin.add("draggable", "cursor", {
	start: function(event, ui) {
		var t = $('body'), o = $(this).data('draggable').options;
		if (t.css("cursor")) o._cursor = t.css("cursor");
		t.css("cursor", o.cursor);
	},
	stop: function(event, ui) {
		var o = $(this).data('draggable').options;
		if (o._cursor) $('body').css("cursor", o._cursor);
	}
});

$.ui.plugin.add("draggable", "iframeFix", {
	start: function(event, ui) {
		var o = $(this).data('draggable').options;
		$(o.iframeFix === true ? "iframe" : o.iframeFix).each(function() {
			$('<div class="ui-draggable-iframeFix" style="background: #fff;"></div>')
			.css({
				width: this.offsetWidth+"px", height: this.offsetHeight+"px",
				position: "absolute", opacity: "0.001", zIndex: 1000
			})
			.css($(this).offset())
			.appendTo("body");
		});
	},
	stop: function(event, ui) {
		$("div.ui-draggable-iframeFix").each(function() { this.parentNode.removeChild(this); }); //Remove frame helpers
	}
});

$.ui.plugin.add("draggable", "opacity", {
	start: function(event, ui) {
		var t = $(ui.helper), o = $(this).data('draggable').options;
		if(t.css("opacity")) o._opacity = t.css("opacity");
		t.css('opacity', o.opacity);
	},
	stop: function(event, ui) {
		var o = $(this).data('draggable').options;
		if(o._opacity) $(ui.helper).css('opacity', o._opacity);
	}
});

$.ui.plugin.add("draggable", "scroll", {
	start: function(event, ui) {
		var i = $(this).data("draggable");
		if(i.scrollParent[0] != document && i.scrollParent[0].tagName != 'HTML') i.overflowOffset = i.scrollParent.offset();
	},
	drag: function(event, ui) {

		var i = $(this).data("draggable"), o = i.options, scrolled = false;

		if(i.scrollParent[0] != document && i.scrollParent[0].tagName != 'HTML') {

			if(!o.axis || o.axis != 'x') {
				if((i.overflowOffset.top + i.scrollParent[0].offsetHeight) - event.pageY < o.scrollSensitivity)
					i.scrollParent[0].scrollTop = scrolled = i.scrollParent[0].scrollTop + o.scrollSpeed;
				else if(event.pageY - i.overflowOffset.top < o.scrollSensitivity)
					i.scrollParent[0].scrollTop = scrolled = i.scrollParent[0].scrollTop - o.scrollSpeed;
			}

			if(!o.axis || o.axis != 'y') {
				if((i.overflowOffset.left + i.scrollParent[0].offsetWidth) - event.pageX < o.scrollSensitivity)
					i.scrollParent[0].scrollLeft = scrolled = i.scrollParent[0].scrollLeft + o.scrollSpeed;
				else if(event.pageX - i.overflowOffset.left < o.scrollSensitivity)
					i.scrollParent[0].scrollLeft = scrolled = i.scrollParent[0].scrollLeft - o.scrollSpeed;
			}

		} else {

			if(!o.axis || o.axis != 'x') {
				if(event.pageY - $(document).scrollTop() < o.scrollSensitivity)
					scrolled = $(document).scrollTop($(document).scrollTop() - o.scrollSpeed);
				else if($(window).height() - (event.pageY - $(document).scrollTop()) < o.scrollSensitivity)
					scrolled = $(document).scrollTop($(document).scrollTop() + o.scrollSpeed);
			}

			if(!o.axis || o.axis != 'y') {
				if(event.pageX - $(document).scrollLeft() < o.scrollSensitivity)
					scrolled = $(document).scrollLeft($(document).scrollLeft() - o.scrollSpeed);
				else if($(window).width() - (event.pageX - $(document).scrollLeft()) < o.scrollSensitivity)
					scrolled = $(document).scrollLeft($(document).scrollLeft() + o.scrollSpeed);
			}

		}

		if(scrolled !== false && $.ui.ddmanager && !o.dropBehaviour)
			$.ui.ddmanager.prepareOffsets(i, event);

	}
});

$.ui.plugin.add("draggable", "snap", {
	start: function(event, ui) {

		var i = $(this).data("draggable"), o = i.options;
		i.snapElements = [];

		$(o.snap.constructor != String ? ( o.snap.items || ':data(draggable)' ) : o.snap).each(function() {
			var $t = $(this); var $o = $t.offset();
			if(this != i.element[0]) i.snapElements.push({
				item: this,
				width: $t.outerWidth(), height: $t.outerHeight(),
				top: $o.top, left: $o.left
			});
		});

	},
	drag: function(event, ui) {

		var inst = $(this).data("draggable"), o = inst.options;
		var d = o.snapTolerance;

		var x1 = ui.offset.left, x2 = x1 + inst.helperProportions.width,
			y1 = ui.offset.top, y2 = y1 + inst.helperProportions.height;

		for (var i = inst.snapElements.length - 1; i >= 0; i--){

			var l = inst.snapElements[i].left, r = l + inst.snapElements[i].width,
				t = inst.snapElements[i].top, b = t + inst.snapElements[i].height;

			//Yes, I know, this is insane ;)
			if(!((l-d < x1 && x1 < r+d && t-d < y1 && y1 < b+d) || (l-d < x1 && x1 < r+d && t-d < y2 && y2 < b+d) || (l-d < x2 && x2 < r+d && t-d < y1 && y1 < b+d) || (l-d < x2 && x2 < r+d && t-d < y2 && y2 < b+d))) {
				if(inst.snapElements[i].snapping) (inst.options.snap.release && inst.options.snap.release.call(inst.element, event, $.extend(inst._uiHash(), { snapItem: inst.snapElements[i].item })));
				inst.snapElements[i].snapping = false;
				continue;
			}

			if(o.snapMode != 'inner') {
				var ts = Math.abs(t - y2) <= d;
				var bs = Math.abs(b - y1) <= d;
				var ls = Math.abs(l - x2) <= d;
				var rs = Math.abs(r - x1) <= d;
				if(ts) ui.position.top = inst._convertPositionTo("relative", { top: t - inst.helperProportions.height, left: 0 }).top - inst.margins.top;
				if(bs) ui.position.top = inst._convertPositionTo("relative", { top: b, left: 0 }).top - inst.margins.top;
				if(ls) ui.position.left = inst._convertPositionTo("relative", { top: 0, left: l - inst.helperProportions.width }).left - inst.margins.left;
				if(rs) ui.position.left = inst._convertPositionTo("relative", { top: 0, left: r }).left - inst.margins.left;
			}

			var first = (ts || bs || ls || rs);

			if(o.snapMode != 'outer') {
				var ts = Math.abs(t - y1) <= d;
				var bs = Math.abs(b - y2) <= d;
				var ls = Math.abs(l - x1) <= d;
				var rs = Math.abs(r - x2) <= d;
				if(ts) ui.position.top = inst._convertPositionTo("relative", { top: t, left: 0 }).top - inst.margins.top;
				if(bs) ui.position.top = inst._convertPositionTo("relative", { top: b - inst.helperProportions.height, left: 0 }).top - inst.margins.top;
				if(ls) ui.position.left = inst._convertPositionTo("relative", { top: 0, left: l }).left - inst.margins.left;
				if(rs) ui.position.left = inst._convertPositionTo("relative", { top: 0, left: r - inst.helperProportions.width }).left - inst.margins.left;
			}

			if(!inst.snapElements[i].snapping && (ts || bs || ls || rs || first))
				(inst.options.snap.snap && inst.options.snap.snap.call(inst.element, event, $.extend(inst._uiHash(), { snapItem: inst.snapElements[i].item })));
			inst.snapElements[i].snapping = (ts || bs || ls || rs || first);

		};

	}
});

$.ui.plugin.add("draggable", "stack", {
	start: function(event, ui) {

		var o = $(this).data("draggable").options;

		var group = $.makeArray($(o.stack)).sort(function(a,b) {
			return (parseInt($(a).css("zIndex"),10) || 0) - (parseInt($(b).css("zIndex"),10) || 0);
		});
		if (!group.length) { return; }
		
		var min = parseInt(group[0].style.zIndex) || 0;
		$(group).each(function(i) {
			this.style.zIndex = min + i;
		});

		this[0].style.zIndex = min + group.length;

	}
});

$.ui.plugin.add("draggable", "zIndex", {
	start: function(event, ui) {
		var t = $(ui.helper), o = $(this).data("draggable").options;
		if(t.css("zIndex")) o._zIndex = t.css("zIndex");
		t.css('zIndex', o.zIndex);
	},
	stop: function(event, ui) {
		var o = $(this).data("draggable").options;
		if(o._zIndex) $(ui.helper).css('zIndex', o._zIndex);
	}
});

})(jQuery);
/*
 * jQuery UI Dialog 1.8.12
 *
 * Copyright 2011, AUTHORS.txt (http://jqueryui.com/about)
 * Dual licensed under the MIT or GPL Version 2 licenses.
 * http://jquery.org/license
 *
 * http://docs.jquery.com/UI/Dialog
 *
 * Depends:
 *	jquery.ui.core.js
 *	jquery.ui.widget.js
 *  jquery.ui.button.js
 *	jquery.ui.draggable.js
 *	jquery.ui.mouse.js
 *	jquery.ui.position.js
 *	jquery.ui.resizable.js
 */
(function( $, undefined ) {

var uiDialogClasses =
		'ui-dialog ' +
		'ui-widget ' +
		'ui-widget-content ' +
		'ui-corner-all ',
	sizeRelatedOptions = {
		buttons: true,
		height: true,
		maxHeight: true,
		maxWidth: true,
		minHeight: true,
		minWidth: true,
		width: true
	},
	resizableRelatedOptions = {
		maxHeight: true,
		maxWidth: true,
		minHeight: true,
		minWidth: true
	},
	// support for jQuery 1.3.2 - handle common attrFn methods for dialog
	attrFn = $.attrFn || {
		val: true,
		css: true,
		html: true,
		text: true,
		data: true,
		width: true,
		height: true,
		offset: true,
		click: true
	};

$.widget("ui.dialog", {
	options: {
		autoOpen: true,
		buttons: {},
		closeOnEscape: true,
		closeText: 'close',
		dialogClass: '',
		draggable: true,
		hide: null,
		height: 'auto',
		maxHeight: false,
		maxWidth: false,
		minHeight: 150,
		minWidth: 150,
		modal: false,
		position: {
			my: 'center',
			at: 'center',
			collision: 'fit',
			// ensure that the titlebar is never outside the document
			using: function(pos) {
				var topOffset = $(this).css(pos).offset().top;
				if (topOffset < 0) {
					$(this).css('top', pos.top - topOffset);
				}
			}
		},
		resizable: true,
		show: null,
		stack: true,
		title: '',
		width: 300,
		zIndex: 1000
	},

	_create: function() {
		this.originalTitle = this.element.attr('title');
		// #5742 - .attr() might return a DOMElement
		if ( typeof this.originalTitle !== "string" ) {
			this.originalTitle = "";
		}

		this.options.title = this.options.title || this.originalTitle;
		var self = this,
			options = self.options,

			title = options.title || '&#160;',
			titleId = $.ui.dialog.getTitleId(self.element),

			uiDialog = (self.uiDialog = $('<div></div>'))
				.appendTo(document.body)
				.hide()
				.addClass(uiDialogClasses + options.dialogClass)
				.css({
					zIndex: options.zIndex
				})
				// setting tabIndex makes the div focusable
				// setting outline to 0 prevents a border on focus in Mozilla
				.attr('tabIndex', -1).css('outline', 0).keydown(function(event) {
					if (options.closeOnEscape && event.keyCode &&
						event.keyCode === $.ui.keyCode.ESCAPE) {
						
						self.close(event);
						event.preventDefault();
					}
				})
				.attr({
					role: 'dialog',
					'aria-labelledby': titleId
				})
				.mousedown(function(event) {
					self.moveToTop(false, event);
				}),

			uiDialogContent = self.element
				.show()
				.removeAttr('title')
				.addClass(
					'ui-dialog-content ' +
					'ui-widget-content')
				.appendTo(uiDialog),

			uiDialogTitlebar = (self.uiDialogTitlebar = $('<div></div>'))
				.addClass(
					'ui-dialog-titlebar ' +
					'ui-widget-header ' +
					'ui-corner-all ' +
					'ui-helper-clearfix'
				)
				.prependTo(uiDialog),

			uiDialogTitlebarClose = $('<a href="#"></a>')
				.addClass(
					'ui-dialog-titlebar-close ' +
					'ui-corner-all'
				)
				.attr('role', 'button')
				.hover(
					function() {
						uiDialogTitlebarClose.addClass('ui-state-hover');
					},
					function() {
						uiDialogTitlebarClose.removeClass('ui-state-hover');
					}
				)
				.focus(function() {
					uiDialogTitlebarClose.addClass('ui-state-focus');
				})
				.blur(function() {
					uiDialogTitlebarClose.removeClass('ui-state-focus');
				})
				.click(function(event) {
					self.close(event);
					return false;
				})
				.appendTo(uiDialogTitlebar),

			uiDialogTitlebarCloseText = (self.uiDialogTitlebarCloseText = $('<span></span>'))
				.addClass(
					'ui-icon ' +
					'ui-icon-closethick'
				)
				.text(options.closeText)
				.appendTo(uiDialogTitlebarClose),

			uiDialogTitle = $('<span></span>')
				.addClass('ui-dialog-title')
				.attr('id', titleId)
				.html(title)
				.prependTo(uiDialogTitlebar);

		//handling of deprecated beforeclose (vs beforeClose) option
		//Ticket #4669 http://dev.jqueryui.com/ticket/4669
		//TODO: remove in 1.9pre
		if ($.isFunction(options.beforeclose) && !$.isFunction(options.beforeClose)) {
			options.beforeClose = options.beforeclose;
		}

		uiDialogTitlebar.find("*").add(uiDialogTitlebar).disableSelection();

		if (options.draggable && $.fn.draggable) {
			self._makeDraggable();
		}
		if (options.resizable && $.fn.resizable) {
			self._makeResizable();
		}

		self._createButtons(options.buttons);
		self._isOpen = false;

		if ($.fn.bgiframe) {
			uiDialog.bgiframe();
		}
	},

	_init: function() {
		if ( this.options.autoOpen ) {
			this.open();
		}
	},

	destroy: function() {
		var self = this;
		
		if (self.overlay) {
			self.overlay.destroy();
		}
		self.uiDialog.hide();
		self.element
			.unbind('.dialog')
			.removeData('dialog')
			.removeClass('ui-dialog-content ui-widget-content')
			.hide().appendTo('body');
		self.uiDialog.remove();

		if (self.originalTitle) {
			self.element.attr('title', self.originalTitle);
		}

		return self;
	},

	widget: function() {
		return this.uiDialog;
	},

	close: function(event) {
		var self = this,
			maxZ, thisZ;
		
		if (false === self._trigger('beforeClose', event)) {
			return;
		}

		if (self.overlay) {
			self.overlay.destroy();
		}
		self.uiDialog.unbind('keypress.ui-dialog');

		self._isOpen = false;

		if (self.options.hide) {
			self.uiDialog.hide(self.options.hide, function() {
				self._trigger('close', event);
			});
		} else {
			self.uiDialog.hide();
			self._trigger('close', event);
		}

		$.ui.dialog.overlay.resize();

		// adjust the maxZ to allow other modal dialogs to continue to work (see #4309)
		if (self.options.modal) {
			maxZ = 0;
			$('.ui-dialog').each(function() {
				if (this !== self.uiDialog[0]) {
					thisZ = $(this).css('z-index');
					if(!isNaN(thisZ)) {
						maxZ = Math.max(maxZ, thisZ);
					}
				}
			});
			$.ui.dialog.maxZ = maxZ;
		}

		return self;
	},

	isOpen: function() {
		return this._isOpen;
	},

	// the force parameter allows us to move modal dialogs to their correct
	// position on open
	moveToTop: function(force, event) {
		var self = this,
			options = self.options,
			saveScroll;

		if ((options.modal && !force) ||
			(!options.stack && !options.modal)) {
			return self._trigger('focus', event);
		}

		if (options.zIndex > $.ui.dialog.maxZ) {
			$.ui.dialog.maxZ = options.zIndex;
		}
		if (self.overlay) {
			$.ui.dialog.maxZ += 1;
			self.overlay.$el.css('z-index', $.ui.dialog.overlay.maxZ = $.ui.dialog.maxZ);
		}

		//Save and then restore scroll since Opera 9.5+ resets when parent z-Index is changed.
		//  http://ui.jquery.com/bugs/ticket/3193
		saveScroll = { scrollTop: self.element.attr('scrollTop'), scrollLeft: self.element.attr('scrollLeft') };
		$.ui.dialog.maxZ += 1;
		self.uiDialog.css('z-index', $.ui.dialog.maxZ);
		self.element.attr(saveScroll);
		self._trigger('focus', event);

		return self;
	},

	open: function() {
		if (this._isOpen) { return; }

		var self = this,
			options = self.options,
			uiDialog = self.uiDialog;

		self.overlay = options.modal ? new $.ui.dialog.overlay(self) : null;
		self._size();
		self._position(options.position);
		uiDialog.show(options.show);
		self.moveToTop(true);

		// prevent tabbing out of modal dialogs
		if (options.modal) {
			uiDialog.bind('keypress.ui-dialog', function(event) {
				if (event.keyCode !== $.ui.keyCode.TAB) {
					return;
				}

				var tabbables = $(':tabbable', this),
					first = tabbables.filter(':first'),
					last  = tabbables.filter(':last');

				if (event.target === last[0] && !event.shiftKey) {
					first.focus(1);
					return false;
				} else if (event.target === first[0] && event.shiftKey) {
					last.focus(1);
					return false;
				}
			});
		}

		// set focus to the first tabbable element in the content area or the first button
		// if there are no tabbable elements, set focus on the dialog itself
		$(self.element.find(':tabbable').get().concat(
			uiDialog.find('.ui-dialog-buttonpane :tabbable').get().concat(
				uiDialog.get()))).eq(0).focus();

		self._isOpen = true;
		self._trigger('open');

		return self;
	},

	_createButtons: function(buttons) {
		var self = this,
			hasButtons = false,
			uiDialogButtonPane = $('<div></div>')
				.addClass(
					'ui-dialog-buttonpane ' +
					'ui-widget-content ' +
					'ui-helper-clearfix'
				),
			uiButtonSet = $( "<div></div>" )
				.addClass( "ui-dialog-buttonset" )
				.appendTo( uiDialogButtonPane );

		// if we already have a button pane, remove it
		self.uiDialog.find('.ui-dialog-buttonpane').remove();

		if (typeof buttons === 'object' && buttons !== null) {
			$.each(buttons, function() {
				return !(hasButtons = true);
			});
		}
		if (hasButtons) {
			$.each(buttons, function(name, props) {
				props = $.isFunction( props ) ?
					{ click: props, text: name } :
					props;
				var button = $('<button type="button"></button>')
					.click(function() {
						props.click.apply(self.element[0], arguments);
					})
					.appendTo(uiButtonSet);
				// can't use .attr( props, true ) with jQuery 1.3.2.
				$.each( props, function( key, value ) {
					if ( key === "click" ) {
						return;
					}
					if ( key in attrFn ) {
						button[ key ]( value );
					} else {
						button.attr( key, value );
					}
				});
				if ($.fn.button) {
					button.button();
				}
			});
			uiDialogButtonPane.appendTo(self.uiDialog);
		}
	},

	_makeDraggable: function() {
		var self = this,
			options = self.options,
			doc = $(document),
			heightBeforeDrag;

		function filteredUi(ui) {
			return {
				position: ui.position,
				offset: ui.offset
			};
		}

		self.uiDialog.draggable({
			cancel: '.ui-dialog-content, .ui-dialog-titlebar-close',
			handle: '.ui-dialog-titlebar',
			containment: 'document',
			start: function(event, ui) {
				heightBeforeDrag = options.height === "auto" ? "auto" : $(this).height();
				$(this).height($(this).height()).addClass("ui-dialog-dragging");
				self._trigger('dragStart', event, filteredUi(ui));
			},
			drag: function(event, ui) {
				self._trigger('drag', event, filteredUi(ui));
			},
			stop: function(event, ui) {
				options.position = [ui.position.left - doc.scrollLeft(),
					ui.position.top - doc.scrollTop()];
				$(this).removeClass("ui-dialog-dragging").height(heightBeforeDrag);
				self._trigger('dragStop', event, filteredUi(ui));
				$.ui.dialog.overlay.resize();
			}
		});
	},

	_makeResizable: function(handles) {
		handles = (handles === undefined ? this.options.resizable : handles);
		var self = this,
			options = self.options,
			// .ui-resizable has position: relative defined in the stylesheet
			// but dialogs have to use absolute or fixed positioning
			position = self.uiDialog.css('position'),
			resizeHandles = (typeof handles === 'string' ?
				handles	:
				'n,e,s,w,se,sw,ne,nw'
			);

		function filteredUi(ui) {
			return {
				originalPosition: ui.originalPosition,
				originalSize: ui.originalSize,
				position: ui.position,
				size: ui.size
			};
		}

		self.uiDialog.resizable({
			cancel: '.ui-dialog-content',
			containment: 'document',
			alsoResize: self.element,
			maxWidth: options.maxWidth,
			maxHeight: options.maxHeight,
			minWidth: options.minWidth,
			minHeight: self._minHeight(),
			handles: resizeHandles,
			start: function(event, ui) {
				$(this).addClass("ui-dialog-resizing");
				self._trigger('resizeStart', event, filteredUi(ui));
			},
			resize: function(event, ui) {
				self._trigger('resize', event, filteredUi(ui));
			},
			stop: function(event, ui) {
				$(this).removeClass("ui-dialog-resizing");
				options.height = $(this).height();
				options.width = $(this).width();
				self._trigger('resizeStop', event, filteredUi(ui));
				$.ui.dialog.overlay.resize();
			}
		})
		.css('position', position)
		.find('.ui-resizable-se').addClass('ui-icon ui-icon-grip-diagonal-se');
	},

	_minHeight: function() {
		var options = this.options;

		if (options.height === 'auto') {
			return options.minHeight;
		} else {
			return Math.min(options.minHeight, options.height);
		}
	},

	_position: function(position) {
		var myAt = [],
			offset = [0, 0],
			isVisible;

		if (position) {
			// deep extending converts arrays to objects in jQuery <= 1.3.2 :-(
	//		if (typeof position == 'string' || $.isArray(position)) {
	//			myAt = $.isArray(position) ? position : position.split(' ');

			if (typeof position === 'string' || (typeof position === 'object' && '0' in position)) {
				myAt = position.split ? position.split(' ') : [position[0], position[1]];
				if (myAt.length === 1) {
					myAt[1] = myAt[0];
				}

				$.each(['left', 'top'], function(i, offsetPosition) {
					if (+myAt[i] === myAt[i]) {
						offset[i] = myAt[i];
						myAt[i] = offsetPosition;
					}
				});

				position = {
					my: myAt.join(" "),
					at: myAt.join(" "),
					offset: offset.join(" ")
				};
			} 

			position = $.extend({}, $.ui.dialog.prototype.options.position, position);
		} else {
			position = $.ui.dialog.prototype.options.position;
		}

		// need to show the dialog to get the actual offset in the position plugin
		isVisible = this.uiDialog.is(':visible');
		if (!isVisible) {
			this.uiDialog.show();
		}
		this.uiDialog
			// workaround for jQuery bug #5781 http://dev.jquery.com/ticket/5781
			.css({ top: 0, left: 0 })
			.position($.extend({ of: window }, position));
		if (!isVisible) {
			this.uiDialog.hide();
		}
	},

	_setOptions: function( options ) {
		var self = this,
			resizableOptions = {},
			resize = false;

		$.each( options, function( key, value ) {
			self._setOption( key, value );
			
			if ( key in sizeRelatedOptions ) {
				resize = true;
			}
			if ( key in resizableRelatedOptions ) {
				resizableOptions[ key ] = value;
			}
		});

		if ( resize ) {
			this._size();
		}
		if ( this.uiDialog.is( ":data(resizable)" ) ) {
			this.uiDialog.resizable( "option", resizableOptions );
		}
	},

	_setOption: function(key, value){
		var self = this,
			uiDialog = self.uiDialog;

		switch (key) {
			//handling of deprecated beforeclose (vs beforeClose) option
			//Ticket #4669 http://dev.jqueryui.com/ticket/4669
			//TODO: remove in 1.9pre
			case "beforeclose":
				key = "beforeClose";
				break;
			case "buttons":
				self._createButtons(value);
				break;
			case "closeText":
				// ensure that we always pass a string
				self.uiDialogTitlebarCloseText.text("" + value);
				break;
			case "dialogClass":
				uiDialog
					.removeClass(self.options.dialogClass)
					.addClass(uiDialogClasses + value);
				break;
			case "disabled":
				if (value) {
					uiDialog.addClass('ui-dialog-disabled');
				} else {
					uiDialog.removeClass('ui-dialog-disabled');
				}
				break;
			case "draggable":
				var isDraggable = uiDialog.is( ":data(draggable)" );
				if ( isDraggable && !value ) {
					uiDialog.draggable( "destroy" );
				}
				
				if ( !isDraggable && value ) {
					self._makeDraggable();
				}
				break;
			case "position":
				self._position(value);
				break;
			case "resizable":
				// currently resizable, becoming non-resizable
				var isResizable = uiDialog.is( ":data(resizable)" );
				if (isResizable && !value) {
					uiDialog.resizable('destroy');
				}

				// currently resizable, changing handles
				if (isResizable && typeof value === 'string') {
					uiDialog.resizable('option', 'handles', value);
				}

				// currently non-resizable, becoming resizable
				if (!isResizable && value !== false) {
					self._makeResizable(value);
				}
				break;
			case "title":
				// convert whatever was passed in o a string, for html() to not throw up
				$(".ui-dialog-title", self.uiDialogTitlebar).html("" + (value || '&#160;'));
				break;
		}

		$.Widget.prototype._setOption.apply(self, arguments);
	},

	_size: function() {
		/* If the user has resized the dialog, the .ui-dialog and .ui-dialog-content
		 * divs will both have width and height set, so we need to reset them
		 */
		var options = this.options,
			nonContentHeight,
			minContentHeight,
			isVisible = this.uiDialog.is( ":visible" );

		// reset content sizing
		this.element.show().css({
			width: 'auto',
			minHeight: 0,
			height: 0
		});

		if (options.minWidth > options.width) {
			options.width = options.minWidth;
		}

		// reset wrapper sizing
		// determine the height of all the non-content elements
		nonContentHeight = this.uiDialog.css({
				height: 'auto',
				width: options.width
			})
			.height();
		minContentHeight = Math.max( 0, options.minHeight - nonContentHeight );
		
		if ( options.height === "auto" ) {
			// only needed for IE6 support
			if ( $.support.minHeight ) {
				this.element.css({
					minHeight: minContentHeight,
					height: "auto"
				});
			} else {
				this.uiDialog.show();
				var autoHeight = this.element.css( "height", "auto" ).height();
				if ( !isVisible ) {
					this.uiDialog.hide();
				}
				this.element.height( Math.max( autoHeight, minContentHeight ) );
			}
		} else {
			this.element.height( Math.max( options.height - nonContentHeight, 0 ) );
		}

		if (this.uiDialog.is(':data(resizable)')) {
			this.uiDialog.resizable('option', 'minHeight', this._minHeight());
		}
	}
});

$.extend($.ui.dialog, {
	version: "1.8.12",

	uuid: 0,
	maxZ: 0,

	getTitleId: function($el) {
		var id = $el.attr('id');
		if (!id) {
			this.uuid += 1;
			id = this.uuid;
		}
		return 'ui-dialog-title-' + id;
	},

	overlay: function(dialog) {
		this.$el = $.ui.dialog.overlay.create(dialog);
	}
});

$.extend($.ui.dialog.overlay, {
	instances: [],
	// reuse old instances due to IE memory leak with alpha transparency (see #5185)
	oldInstances: [],
	maxZ: 0,
	events: $.map('focus,mousedown,mouseup,keydown,keypress,click'.split(','),
		function(event) { return event + '.dialog-overlay'; }).join(' '),
	create: function(dialog) {
		if (this.instances.length === 0) {
			// prevent use of anchors and inputs
			// we use a setTimeout in case the overlay is created from an
			// event that we're going to be cancelling (see #2804)
			setTimeout(function() {
				// handle $(el).dialog().dialog('close') (see #4065)
				if ($.ui.dialog.overlay.instances.length) {
					$(document).bind($.ui.dialog.overlay.events, function(event) {
						// stop events if the z-index of the target is < the z-index of the overlay
						// we cannot return true when we don't want to cancel the event (#3523)
						if ($(event.target).zIndex() < $.ui.dialog.overlay.maxZ) {
							return false;
						}
					});
				}
			}, 1);

			// allow closing by pressing the escape key
			$(document).bind('keydown.dialog-overlay', function(event) {
				if (dialog.options.closeOnEscape && event.keyCode &&
					event.keyCode === $.ui.keyCode.ESCAPE) {
					
					dialog.close(event);
					event.preventDefault();
				}
			});

			// handle window resize
			$(window).bind('resize.dialog-overlay', $.ui.dialog.overlay.resize);
		}

		var $el = (this.oldInstances.pop() || $('<div></div>').addClass('ui-widget-overlay'))
			.appendTo(document.body)
			.css({
				width: this.width(),
				height: this.height()
			});

		if ($.fn.bgiframe) {
			$el.bgiframe();
		}

		this.instances.push($el);
		return $el;
	},

	destroy: function($el) {
		var indexOf = $.inArray($el, this.instances);
		if (indexOf != -1){
			this.oldInstances.push(this.instances.splice(indexOf, 1)[0]);
		}

		if (this.instances.length === 0) {
			$([document, window]).unbind('.dialog-overlay');
		}

		$el.remove();
		
		// adjust the maxZ to allow other modal dialogs to continue to work (see #4309)
		var maxZ = 0;
		$.each(this.instances, function() {
			maxZ = Math.max(maxZ, this.css('z-index'));
		});
		this.maxZ = maxZ;
	},

	height: function() {
		var scrollHeight,
			offsetHeight;
		// handle IE 6
		if ($.browser.msie && $.browser.version < 7) {
			scrollHeight = Math.max(
				document.documentElement.scrollHeight,
				document.body.scrollHeight
			);
			offsetHeight = Math.max(
				document.documentElement.offsetHeight,
				document.body.offsetHeight
			);

			if (scrollHeight < offsetHeight) {
				return $(window).height() + 'px';
			} else {
				return scrollHeight + 'px';
			}
		// handle "good" browsers
		} else {
			return $(document).height() + 'px';
		}
	},

	width: function() {
		var scrollWidth,
			offsetWidth;
		// handle IE 6
		if ($.browser.msie && $.browser.version < 7) {
			scrollWidth = Math.max(
				document.documentElement.scrollWidth,
				document.body.scrollWidth
			);
			offsetWidth = Math.max(
				document.documentElement.offsetWidth,
				document.body.offsetWidth
			);

			if (scrollWidth < offsetWidth) {
				return $(window).width() + 'px';
			} else {
				return scrollWidth + 'px';
			}
		// handle "good" browsers
		} else {
			return $(document).width() + 'px';
		}
	},

	resize: function() {
		/* If the dialog is draggable and the user drags it past the
		 * right edge of the window, the document becomes wider so we
		 * need to stretch the overlay. If the user then drags the
		 * dialog back to the left, the document will become narrower,
		 * so we need to shrink the overlay to the appropriate size.
		 * This is handled by shrinking the overlay before setting it
		 * to the full document size.
		 */
		var $overlays = $([]);
		$.each($.ui.dialog.overlay.instances, function() {
			$overlays = $overlays.add(this);
		});

		$overlays.css({
			width: 0,
			height: 0
		}).css({
			width: $.ui.dialog.overlay.width(),
			height: $.ui.dialog.overlay.height()
		});
	}
});

$.extend($.ui.dialog.overlay.prototype, {
	destroy: function() {
		$.ui.dialog.overlay.destroy(this.$el);
	}
});

}(jQuery));
/*
 * jQuery UI Slider 1.8.12
 *
 * Copyright 2011, AUTHORS.txt (http://jqueryui.com/about)
 * Dual licensed under the MIT or GPL Version 2 licenses.
 * http://jquery.org/license
 *
 * http://docs.jquery.com/UI/Slider
 *
 * Depends:
 *	jquery.ui.core.js
 *	jquery.ui.mouse.js
 *	jquery.ui.widget.js
 */
(function( $, undefined ) {

// number of pages in a slider
// (how many times can you page up/down to go through the whole range)
var numPages = 5;

$.widget( "ui.slider", $.ui.mouse, {

	widgetEventPrefix: "slide",

	options: {
		animate: false,
		distance: 0,
		max: 100,
		min: 0,
		orientation: "horizontal",
		range: false,
		step: 1,
		value: 0,
		values: null
	},

	_create: function() {
		var self = this,
			o = this.options;

		this._keySliding = false;
		this._mouseSliding = false;
		this._animateOff = true;
		this._handleIndex = null;
		this._detectOrientation();
		this._mouseInit();

		this.element
			.addClass( "ui-slider" +
				" ui-slider-" + this.orientation +
				" ui-widget" +
				" ui-widget-content" +
				" ui-corner-all" );
		
		if ( o.disabled ) {
			this.element.addClass( "ui-slider-disabled ui-disabled" );
		}

		this.range = $([]);

		if ( o.range ) {
			if ( o.range === true ) {
				this.range = $( "<div></div>" );
				if ( !o.values ) {
					o.values = [ this._valueMin(), this._valueMin() ];
				}
				if ( o.values.length && o.values.length !== 2 ) {
					o.values = [ o.values[0], o.values[0] ];
				}
			} else {
				this.range = $( "<div></div>" );
			}

			this.range
				.appendTo( this.element )
				.addClass( "ui-slider-range" );

			if ( o.range === "min" || o.range === "max" ) {
				this.range.addClass( "ui-slider-range-" + o.range );
			}

			// note: this isn't the most fittingly semantic framework class for this element,
			// but worked best visually with a variety of themes
			this.range.addClass( "ui-widget-header" );
		}

		if ( $( ".ui-slider-handle", this.element ).length === 0 ) {
			$( "<a href='#'></a>" )
				.appendTo( this.element )
				.addClass( "ui-slider-handle" );
		}

		if ( o.values && o.values.length ) {
			while ( $(".ui-slider-handle", this.element).length < o.values.length ) {
				$( "<a href='#'></a>" )
					.appendTo( this.element )
					.addClass( "ui-slider-handle" );
			}
		}

		this.handles = $( ".ui-slider-handle", this.element )
			.addClass( "ui-state-default" +
				" ui-corner-all" );

		this.handle = this.handles.eq( 0 );

		this.handles.add( this.range ).filter( "a" )
			.click(function( event ) {
				event.preventDefault();
			})
			.hover(function() {
				if ( !o.disabled ) {
					$( this ).addClass( "ui-state-hover" );
				}
			}, function() {
				$( this ).removeClass( "ui-state-hover" );
			})
			.focus(function() {
				if ( !o.disabled ) {
					$( ".ui-slider .ui-state-focus" ).removeClass( "ui-state-focus" );
					$( this ).addClass( "ui-state-focus" );
				} else {
					$( this ).blur();
				}
			})
			.blur(function() {
				$( this ).removeClass( "ui-state-focus" );
			});

		this.handles.each(function( i ) {
			$( this ).data( "index.ui-slider-handle", i );
		});

		this.handles
			.keydown(function( event ) {
				var ret = true,
					index = $( this ).data( "index.ui-slider-handle" ),
					allowed,
					curVal,
					newVal,
					step;
	
				if ( self.options.disabled ) {
					return;
				}
	
				switch ( event.keyCode ) {
					case $.ui.keyCode.HOME:
					case $.ui.keyCode.END:
					case $.ui.keyCode.PAGE_UP:
					case $.ui.keyCode.PAGE_DOWN:
					case $.ui.keyCode.UP:
					case $.ui.keyCode.RIGHT:
					case $.ui.keyCode.DOWN:
					case $.ui.keyCode.LEFT:
						ret = false;
						if ( !self._keySliding ) {
							self._keySliding = true;
							$( this ).addClass( "ui-state-active" );
							allowed = self._start( event, index );
							if ( allowed === false ) {
								return;
							}
						}
						break;
				}
	
				step = self.options.step;
				if ( self.options.values && self.options.values.length ) {
					curVal = newVal = self.values( index );
				} else {
					curVal = newVal = self.value();
				}
	
				switch ( event.keyCode ) {
					case $.ui.keyCode.HOME:
						newVal = self._valueMin();
						break;
					case $.ui.keyCode.END:
						newVal = self._valueMax();
						break;
					case $.ui.keyCode.PAGE_UP:
						newVal = self._trimAlignValue( curVal + ( (self._valueMax() - self._valueMin()) / numPages ) );
						break;
					case $.ui.keyCode.PAGE_DOWN:
						newVal = self._trimAlignValue( curVal - ( (self._valueMax() - self._valueMin()) / numPages ) );
						break;
					case $.ui.keyCode.UP:
					case $.ui.keyCode.RIGHT:
						if ( curVal === self._valueMax() ) {
							return;
						}
						newVal = self._trimAlignValue( curVal + step );
						break;
					case $.ui.keyCode.DOWN:
					case $.ui.keyCode.LEFT:
						if ( curVal === self._valueMin() ) {
							return;
						}
						newVal = self._trimAlignValue( curVal - step );
						break;
				}
	
				self._slide( event, index, newVal );
	
				return ret;
	
			})
			.keyup(function( event ) {
				var index = $( this ).data( "index.ui-slider-handle" );
	
				if ( self._keySliding ) {
					self._keySliding = false;
					self._stop( event, index );
					self._change( event, index );
					$( this ).removeClass( "ui-state-active" );
				}
	
			});

		this._refreshValue();

		this._animateOff = false;
	},

	destroy: function() {
		this.handles.remove();
		this.range.remove();

		this.element
			.removeClass( "ui-slider" +
				" ui-slider-horizontal" +
				" ui-slider-vertical" +
				" ui-slider-disabled" +
				" ui-widget" +
				" ui-widget-content" +
				" ui-corner-all" )
			.removeData( "slider" )
			.unbind( ".slider" );

		this._mouseDestroy();

		return this;
	},

	_mouseCapture: function( event ) {
		var o = this.options,
			position,
			normValue,
			distance,
			closestHandle,
			self,
			index,
			allowed,
			offset,
			mouseOverHandle;

		if ( o.disabled ) {
			return false;
		}

		this.elementSize = {
			width: this.element.outerWidth(),
			height: this.element.outerHeight()
		};
		this.elementOffset = this.element.offset();

		position = { x: event.pageX, y: event.pageY };
		normValue = this._normValueFromMouse( position );
		distance = this._valueMax() - this._valueMin() + 1;
		self = this;
		this.handles.each(function( i ) {
			var thisDistance = Math.abs( normValue - self.values(i) );
			if ( distance > thisDistance ) {
				distance = thisDistance;
				closestHandle = $( this );
				index = i;
			}
		});

		// workaround for bug #3736 (if both handles of a range are at 0,
		// the first is always used as the one with least distance,
		// and moving it is obviously prevented by preventing negative ranges)
		if( o.range === true && this.values(1) === o.min ) {
			index += 1;
			closestHandle = $( this.handles[index] );
		}

		allowed = this._start( event, index );
		if ( allowed === false ) {
			return false;
		}
		this._mouseSliding = true;

		self._handleIndex = index;

		closestHandle
			.addClass( "ui-state-active" )
			.focus();
		
		offset = closestHandle.offset();
		mouseOverHandle = !$( event.target ).parents().andSelf().is( ".ui-slider-handle" );
		this._clickOffset = mouseOverHandle ? { left: 0, top: 0 } : {
			left: event.pageX - offset.left - ( closestHandle.width() / 2 ),
			top: event.pageY - offset.top -
				( closestHandle.height() / 2 ) -
				( parseInt( closestHandle.css("borderTopWidth"), 10 ) || 0 ) -
				( parseInt( closestHandle.css("borderBottomWidth"), 10 ) || 0) +
				( parseInt( closestHandle.css("marginTop"), 10 ) || 0)
		};

		if ( !this.handles.hasClass( "ui-state-hover" ) ) {
			this._slide( event, index, normValue );
		}
		this._animateOff = true;
		return true;
	},

	_mouseStart: function( event ) {
		return true;
	},

	_mouseDrag: function( event ) {
		var position = { x: event.pageX, y: event.pageY },
			normValue = this._normValueFromMouse( position );
		
		this._slide( event, this._handleIndex, normValue );

		return false;
	},

	_mouseStop: function( event ) {
		this.handles.removeClass( "ui-state-active" );
		this._mouseSliding = false;

		this._stop( event, this._handleIndex );
		this._change( event, this._handleIndex );

		this._handleIndex = null;
		this._clickOffset = null;
		this._animateOff = false;

		return false;
	},
	
	_detectOrientation: function() {
		this.orientation = ( this.options.orientation === "vertical" ) ? "vertical" : "horizontal";
	},

	_normValueFromMouse: function( position ) {
		var pixelTotal,
			pixelMouse,
			percentMouse,
			valueTotal,
			valueMouse;

		if ( this.orientation === "horizontal" ) {
			pixelTotal = this.elementSize.width;
			pixelMouse = position.x - this.elementOffset.left - ( this._clickOffset ? this._clickOffset.left : 0 );
		} else {
			pixelTotal = this.elementSize.height;
			pixelMouse = position.y - this.elementOffset.top - ( this._clickOffset ? this._clickOffset.top : 0 );
		}

		percentMouse = ( pixelMouse / pixelTotal );
		if ( percentMouse > 1 ) {
			percentMouse = 1;
		}
		if ( percentMouse < 0 ) {
			percentMouse = 0;
		}
		if ( this.orientation === "vertical" ) {
			percentMouse = 1 - percentMouse;
		}

		valueTotal = this._valueMax() - this._valueMin();
		valueMouse = this._valueMin() + percentMouse * valueTotal;

		return this._trimAlignValue( valueMouse );
	},

	_start: function( event, index ) {
		var uiHash = {
			handle: this.handles[ index ],
			value: this.value()
		};
		if ( this.options.values && this.options.values.length ) {
			uiHash.value = this.values( index );
			uiHash.values = this.values();
		}
		return this._trigger( "start", event, uiHash );
	},

	_slide: function( event, index, newVal ) {
		var otherVal,
			newValues,
			allowed;

		if ( this.options.values && this.options.values.length ) {
			otherVal = this.values( index ? 0 : 1 );

			if ( ( this.options.values.length === 2 && this.options.range === true ) && 
					( ( index === 0 && newVal > otherVal) || ( index === 1 && newVal < otherVal ) )
				) {
				newVal = otherVal;
			}

			if ( newVal !== this.values( index ) ) {
				newValues = this.values();
				newValues[ index ] = newVal;
				// A slide can be canceled by returning false from the slide callback
				allowed = this._trigger( "slide", event, {
					handle: this.handles[ index ],
					value: newVal,
					values: newValues
				} );
				otherVal = this.values( index ? 0 : 1 );
				if ( allowed !== false ) {
					this.values( index, newVal, true );
				}
			}
		} else {
			if ( newVal !== this.value() ) {
				// A slide can be canceled by returning false from the slide callback
				allowed = this._trigger( "slide", event, {
					handle: this.handles[ index ],
					value: newVal
				} );
				if ( allowed !== false ) {
					this.value( newVal );
				}
			}
		}
	},

	_stop: function( event, index ) {
		var uiHash = {
			handle: this.handles[ index ],
			value: this.value()
		};
		if ( this.options.values && this.options.values.length ) {
			uiHash.value = this.values( index );
			uiHash.values = this.values();
		}

		this._trigger( "stop", event, uiHash );
	},

	_change: function( event, index ) {
		if ( !this._keySliding && !this._mouseSliding ) {
			var uiHash = {
				handle: this.handles[ index ],
				value: this.value()
			};
			if ( this.options.values && this.options.values.length ) {
				uiHash.value = this.values( index );
				uiHash.values = this.values();
			}

			this._trigger( "change", event, uiHash );
		}
	},

	value: function( newValue ) {
		if ( arguments.length ) {
			this.options.value = this._trimAlignValue( newValue );
			this._refreshValue();
			this._change( null, 0 );
			return;
		}

		return this._value();
	},

	values: function( index, newValue ) {
		var vals,
			newValues,
			i;

		if ( arguments.length > 1 ) {
			this.options.values[ index ] = this._trimAlignValue( newValue );
			this._refreshValue();
			this._change( null, index );
			return;
		}

		if ( arguments.length ) {
			if ( $.isArray( arguments[ 0 ] ) ) {
				vals = this.options.values;
				newValues = arguments[ 0 ];
				for ( i = 0; i < vals.length; i += 1 ) {
					vals[ i ] = this._trimAlignValue( newValues[ i ] );
					this._change( null, i );
				}
				this._refreshValue();
			} else {
				if ( this.options.values && this.options.values.length ) {
					return this._values( index );
				} else {
					return this.value();
				}
			}
		} else {
			return this._values();
		}
	},

	_setOption: function( key, value ) {
		var i,
			valsLength = 0;

		if ( $.isArray( this.options.values ) ) {
			valsLength = this.options.values.length;
		}

		$.Widget.prototype._setOption.apply( this, arguments );

		switch ( key ) {
			case "disabled":
				if ( value ) {
					this.handles.filter( ".ui-state-focus" ).blur();
					this.handles.removeClass( "ui-state-hover" );
					this.handles.attr( "disabled", "disabled" );
					this.element.addClass( "ui-disabled" );
				} else {
					this.handles.removeAttr( "disabled" );
					this.element.removeClass( "ui-disabled" );
				}
				break;
			case "orientation":
				this._detectOrientation();
				this.element
					.removeClass( "ui-slider-horizontal ui-slider-vertical" )
					.addClass( "ui-slider-" + this.orientation );
				this._refreshValue();
				break;
			case "value":
				this._animateOff = true;
				this._refreshValue();
				this._change( null, 0 );
				this._animateOff = false;
				break;
			case "values":
				this._animateOff = true;
				this._refreshValue();
				for ( i = 0; i < valsLength; i += 1 ) {
					this._change( null, i );
				}
				this._animateOff = false;
				break;
		}
	},

	//internal value getter
	// _value() returns value trimmed by min and max, aligned by step
	_value: function() {
		var val = this.options.value;
		val = this._trimAlignValue( val );

		return val;
	},

	//internal values getter
	// _values() returns array of values trimmed by min and max, aligned by step
	// _values( index ) returns single value trimmed by min and max, aligned by step
	_values: function( index ) {
		var val,
			vals,
			i;

		if ( arguments.length ) {
			val = this.options.values[ index ];
			val = this._trimAlignValue( val );

			return val;
		} else {
			// .slice() creates a copy of the array
			// this copy gets trimmed by min and max and then returned
			vals = this.options.values.slice();
			for ( i = 0; i < vals.length; i+= 1) {
				vals[ i ] = this._trimAlignValue( vals[ i ] );
			}

			return vals;
		}
	},
	
	// returns the step-aligned value that val is closest to, between (inclusive) min and max
	_trimAlignValue: function( val ) {
		if ( val <= this._valueMin() ) {
			return this._valueMin();
		}
		if ( val >= this._valueMax() ) {
			return this._valueMax();
		}
		var step = ( this.options.step > 0 ) ? this.options.step : 1,
			valModStep = (val - this._valueMin()) % step;
			alignValue = val - valModStep;

		if ( Math.abs(valModStep) * 2 >= step ) {
			alignValue += ( valModStep > 0 ) ? step : ( -step );
		}

		// Since JavaScript has problems with large floats, round
		// the final value to 5 digits after the decimal point (see #4124)
		return parseFloat( alignValue.toFixed(5) );
	},

	_valueMin: function() {
		return this.options.min;
	},

	_valueMax: function() {
		return this.options.max;
	},
	
	_refreshValue: function() {
		var oRange = this.options.range,
			o = this.options,
			self = this,
			animate = ( !this._animateOff ) ? o.animate : false,
			valPercent,
			_set = {},
			lastValPercent,
			value,
			valueMin,
			valueMax;

		if ( this.options.values && this.options.values.length ) {
			this.handles.each(function( i, j ) {
				valPercent = ( self.values(i) - self._valueMin() ) / ( self._valueMax() - self._valueMin() ) * 100;
				_set[ self.orientation === "horizontal" ? "left" : "bottom" ] = valPercent + "%";
				$( this ).stop( 1, 1 )[ animate ? "animate" : "css" ]( _set, o.animate );
				if ( self.options.range === true ) {
					if ( self.orientation === "horizontal" ) {
						if ( i === 0 ) {
							self.range.stop( 1, 1 )[ animate ? "animate" : "css" ]( { left: valPercent + "%" }, o.animate );
						}
						if ( i === 1 ) {
							self.range[ animate ? "animate" : "css" ]( { width: ( valPercent - lastValPercent ) + "%" }, { queue: false, duration: o.animate } );
						}
					} else {
						if ( i === 0 ) {
							self.range.stop( 1, 1 )[ animate ? "animate" : "css" ]( { bottom: ( valPercent ) + "%" }, o.animate );
						}
						if ( i === 1 ) {
							self.range[ animate ? "animate" : "css" ]( { height: ( valPercent - lastValPercent ) + "%" }, { queue: false, duration: o.animate } );
						}
					}
				}
				lastValPercent = valPercent;
			});
		} else {
			value = this.value();
			valueMin = this._valueMin();
			valueMax = this._valueMax();
			valPercent = ( valueMax !== valueMin ) ?
					( value - valueMin ) / ( valueMax - valueMin ) * 100 :
					0;
			_set[ self.orientation === "horizontal" ? "left" : "bottom" ] = valPercent + "%";
			this.handle.stop( 1, 1 )[ animate ? "animate" : "css" ]( _set, o.animate );

			if ( oRange === "min" && this.orientation === "horizontal" ) {
				this.range.stop( 1, 1 )[ animate ? "animate" : "css" ]( { width: valPercent + "%" }, o.animate );
			}
			if ( oRange === "max" && this.orientation === "horizontal" ) {
				this.range[ animate ? "animate" : "css" ]( { width: ( 100 - valPercent ) + "%" }, { queue: false, duration: o.animate } );
			}
			if ( oRange === "min" && this.orientation === "vertical" ) {
				this.range.stop( 1, 1 )[ animate ? "animate" : "css" ]( { height: valPercent + "%" }, o.animate );
			}
			if ( oRange === "max" && this.orientation === "vertical" ) {
				this.range[ animate ? "animate" : "css" ]( { height: ( 100 - valPercent ) + "%" }, { queue: false, duration: o.animate } );
			}
		}
	}

});

$.extend( $.ui.slider, {
	version: "1.8.12"
});

}(jQuery));
/*
 * jQuery UI Tabs 1.8.12
 *
 * Copyright 2011, AUTHORS.txt (http://jqueryui.com/about)
 * Dual licensed under the MIT or GPL Version 2 licenses.
 * http://jquery.org/license
 *
 * http://docs.jquery.com/UI/Tabs
 *
 * Depends:
 *	jquery.ui.core.js
 *	jquery.ui.widget.js
 */
(function( $, undefined ) {

var tabId = 0,
	listId = 0;

function getNextTabId() {
	return ++tabId;
}

function getNextListId() {
	return ++listId;
}

$.widget( "ui.tabs", {
	options: {
		add: null,
		ajaxOptions: null,
		cache: false,
		cookie: null, // e.g. { expires: 7, path: '/', domain: 'jquery.com', secure: true }
		collapsible: false,
		disable: null,
		disabled: [],
		enable: null,
		event: "click",
		fx: null, // e.g. { height: 'toggle', opacity: 'toggle', duration: 200 }
		idPrefix: "ui-tabs-",
		load: null,
		panelTemplate: "<div></div>",
		remove: null,
		select: null,
		show: null,
		spinner: "<em>Loading&#8230;</em>",
		tabTemplate: "<li><a href='#{href}'><span>#{label}</span></a></li>"
	},

	_create: function() {
		this._tabify( true );
	},

	_setOption: function( key, value ) {
		if ( key == "selected" ) {
			if (this.options.collapsible && value == this.options.selected ) {
				return;
			}
			this.select( value );
		} else {
			this.options[ key ] = value;
			this._tabify();
		}
	},

	_tabId: function( a ) {
		return a.title && a.title.replace( /\s/g, "_" ).replace( /[^\w\u00c0-\uFFFF-]/g, "" ) ||
			this.options.idPrefix + getNextTabId();
	},

	_sanitizeSelector: function( hash ) {
		// we need this because an id may contain a ":"
		return hash.replace( /:/g, "\\:" );
	},

	_cookie: function() {
		var cookie = this.cookie ||
			( this.cookie = this.options.cookie.name || "ui-tabs-" + getNextListId() );
		return $.cookie.apply( null, [ cookie ].concat( $.makeArray( arguments ) ) );
	},

	_ui: function( tab, panel ) {
		return {
			tab: tab,
			panel: panel,
			index: this.anchors.index( tab )
		};
	},

	_cleanup: function() {
		// restore all former loading tabs labels
		this.lis.filter( ".ui-state-processing" )
			.removeClass( "ui-state-processing" )
			.find( "span:data(label.tabs)" )
				.each(function() {
					var el = $( this );
					el.html( el.data( "label.tabs" ) ).removeData( "label.tabs" );
				});
	},

	_tabify: function( init ) {
		var self = this,
			o = this.options,
			fragmentId = /^#.+/; // Safari 2 reports '#' for an empty hash

		this.list = this.element.find( "ol,ul" ).eq( 0 );
		this.lis = $( " > li:has(a[href])", this.list );
		this.anchors = this.lis.map(function() {
			return $( "a", this )[ 0 ];
		});
		this.panels = $( [] );

		this.anchors.each(function( i, a ) {
			var href = $( a ).attr( "href" );
			// For dynamically created HTML that contains a hash as href IE < 8 expands
			// such href to the full page url with hash and then misinterprets tab as ajax.
			// Same consideration applies for an added tab with a fragment identifier
			// since a[href=#fragment-identifier] does unexpectedly not match.
			// Thus normalize href attribute...
			var hrefBase = href.split( "#" )[ 0 ],
				baseEl;
			if ( hrefBase && ( hrefBase === location.toString().split( "#" )[ 0 ] ||
					( baseEl = $( "base" )[ 0 ]) && hrefBase === baseEl.href ) ) {
				href = a.hash;
				a.href = href;
			}

			// inline tab
			if ( fragmentId.test( href ) ) {
				self.panels = self.panels.add( self.element.find( self._sanitizeSelector( href ) ) );
			// remote tab
			// prevent loading the page itself if href is just "#"
			} else if ( href && href !== "#" ) {
				// required for restore on destroy
				$.data( a, "href.tabs", href );

				// TODO until #3808 is fixed strip fragment identifier from url
				// (IE fails to load from such url)
				$.data( a, "load.tabs", href.replace( /#.*$/, "" ) );

				var id = self._tabId( a );
				a.href = "#" + id;
				var $panel = self.element.find( "#" + id );
				if ( !$panel.length ) {
					$panel = $( o.panelTemplate )
						.attr( "id", id )
						.addClass( "ui-tabs-panel ui-widget-content ui-corner-bottom" )
						.insertAfter( self.panels[ i - 1 ] || self.list );
					$panel.data( "destroy.tabs", true );
				}
				self.panels = self.panels.add( $panel );
			// invalid tab href
			} else {
				o.disabled.push( i );
			}
		});

		// initialization from scratch
		if ( init ) {
			// attach necessary classes for styling
			this.element.addClass( "ui-tabs ui-widget ui-widget-content ui-corner-all" );
			this.list.addClass( "ui-tabs-nav ui-helper-reset ui-helper-clearfix ui-widget-header ui-corner-all" );
			this.lis.addClass( "ui-state-default ui-corner-top" );
			this.panels.addClass( "ui-tabs-panel ui-widget-content ui-corner-bottom" );

			// Selected tab
			// use "selected" option or try to retrieve:
			// 1. from fragment identifier in url
			// 2. from cookie
			// 3. from selected class attribute on <li>
			if ( o.selected === undefined ) {
				if ( location.hash ) {
					this.anchors.each(function( i, a ) {
						if ( a.hash == location.hash ) {
							o.selected = i;
							return false;
						}
					});
				}
				if ( typeof o.selected !== "number" && o.cookie ) {
					o.selected = parseInt( self._cookie(), 10 );
				}
				if ( typeof o.selected !== "number" && this.lis.filter( ".ui-tabs-selected" ).length ) {
					o.selected = this.lis.index( this.lis.filter( ".ui-tabs-selected" ) );
				}
				o.selected = o.selected || ( this.lis.length ? 0 : -1 );
			} else if ( o.selected === null ) { // usage of null is deprecated, TODO remove in next release
				o.selected = -1;
			}

			// sanity check - default to first tab...
			o.selected = ( ( o.selected >= 0 && this.anchors[ o.selected ] ) || o.selected < 0 )
				? o.selected
				: 0;

			// Take disabling tabs via class attribute from HTML
			// into account and update option properly.
			// A selected tab cannot become disabled.
			o.disabled = $.unique( o.disabled.concat(
				$.map( this.lis.filter( ".ui-state-disabled" ), function( n, i ) {
					return self.lis.index( n );
				})
			) ).sort();

			if ( $.inArray( o.selected, o.disabled ) != -1 ) {
				o.disabled.splice( $.inArray( o.selected, o.disabled ), 1 );
			}

			// highlight selected tab
			this.panels.addClass( "ui-tabs-hide" );
			this.lis.removeClass( "ui-tabs-selected ui-state-active" );
			// check for length avoids error when initializing empty list
			if ( o.selected >= 0 && this.anchors.length ) {
				self.element.find( self._sanitizeSelector( self.anchors[ o.selected ].hash ) ).removeClass( "ui-tabs-hide" );
				this.lis.eq( o.selected ).addClass( "ui-tabs-selected ui-state-active" );

				// seems to be expected behavior that the show callback is fired
				self.element.queue( "tabs", function() {
					self._trigger( "show", null,
						self._ui( self.anchors[ o.selected ], self.element.find( self._sanitizeSelector( self.anchors[ o.selected ].hash ) )[ 0 ] ) );
				});

				this.load( o.selected );
			}

			// clean up to avoid memory leaks in certain versions of IE 6
			// TODO: namespace this event
			$( window ).bind( "unload", function() {
				self.lis.add( self.anchors ).unbind( ".tabs" );
				self.lis = self.anchors = self.panels = null;
			});
		// update selected after add/remove
		} else {
			o.selected = this.lis.index( this.lis.filter( ".ui-tabs-selected" ) );
		}

		// update collapsible
		// TODO: use .toggleClass()
		this.element[ o.collapsible ? "addClass" : "removeClass" ]( "ui-tabs-collapsible" );

		// set or update cookie after init and add/remove respectively
		if ( o.cookie ) {
			this._cookie( o.selected, o.cookie );
		}

		// disable tabs
		for ( var i = 0, li; ( li = this.lis[ i ] ); i++ ) {
			$( li )[ $.inArray( i, o.disabled ) != -1 &&
				// TODO: use .toggleClass()
				!$( li ).hasClass( "ui-tabs-selected" ) ? "addClass" : "removeClass" ]( "ui-state-disabled" );
		}

		// reset cache if switching from cached to not cached
		if ( o.cache === false ) {
			this.anchors.removeData( "cache.tabs" );
		}

		// remove all handlers before, tabify may run on existing tabs after add or option change
		this.lis.add( this.anchors ).unbind( ".tabs" );

		if ( o.event !== "mouseover" ) {
			var addState = function( state, el ) {
				if ( el.is( ":not(.ui-state-disabled)" ) ) {
					el.addClass( "ui-state-" + state );
				}
			};
			var removeState = function( state, el ) {
				el.removeClass( "ui-state-" + state );
			};
			this.lis.bind( "mouseover.tabs" , function() {
				addState( "hover", $( this ) );
			});
			this.lis.bind( "mouseout.tabs", function() {
				removeState( "hover", $( this ) );
			});
			this.anchors.bind( "focus.tabs", function() {
				addState( "focus", $( this ).closest( "li" ) );
			});
			this.anchors.bind( "blur.tabs", function() {
				removeState( "focus", $( this ).closest( "li" ) );
			});
		}

		// set up animations
		var hideFx, showFx;
		if ( o.fx ) {
			if ( $.isArray( o.fx ) ) {
				hideFx = o.fx[ 0 ];
				showFx = o.fx[ 1 ];
			} else {
				hideFx = showFx = o.fx;
			}
		}

		// Reset certain styles left over from animation
		// and prevent IE's ClearType bug...
		function resetStyle( $el, fx ) {
			$el.css( "display", "" );
			if ( !$.support.opacity && fx.opacity ) {
				$el[ 0 ].style.removeAttribute( "filter" );
			}
		}

		// Show a tab...
		var showTab = showFx
			? function( clicked, $show ) {
				$( clicked ).closest( "li" ).addClass( "ui-tabs-selected ui-state-active" );
				$show.hide().removeClass( "ui-tabs-hide" ) // avoid flicker that way
					.animate( showFx, showFx.duration || "normal", function() {
						resetStyle( $show, showFx );
						self._trigger( "show", null, self._ui( clicked, $show[ 0 ] ) );
					});
			}
			: function( clicked, $show ) {
				$( clicked ).closest( "li" ).addClass( "ui-tabs-selected ui-state-active" );
				$show.removeClass( "ui-tabs-hide" );
				self._trigger( "show", null, self._ui( clicked, $show[ 0 ] ) );
			};

		// Hide a tab, $show is optional...
		var hideTab = hideFx
			? function( clicked, $hide ) {
				$hide.animate( hideFx, hideFx.duration || "normal", function() {
					self.lis.removeClass( "ui-tabs-selected ui-state-active" );
					$hide.addClass( "ui-tabs-hide" );
					resetStyle( $hide, hideFx );
					self.element.dequeue( "tabs" );
				});
			}
			: function( clicked, $hide, $show ) {
				self.lis.removeClass( "ui-tabs-selected ui-state-active" );
				$hide.addClass( "ui-tabs-hide" );
				self.element.dequeue( "tabs" );
			};

		// attach tab event handler, unbind to avoid duplicates from former tabifying...
		this.anchors.bind( o.event + ".tabs", function() {
			var el = this,
				$li = $(el).closest( "li" ),
				$hide = self.panels.filter( ":not(.ui-tabs-hide)" ),
				$show = self.element.find( self._sanitizeSelector( el.hash ) );

			// If tab is already selected and not collapsible or tab disabled or
			// or is already loading or click callback returns false stop here.
			// Check if click handler returns false last so that it is not executed
			// for a disabled or loading tab!
			if ( ( $li.hasClass( "ui-tabs-selected" ) && !o.collapsible) ||
				$li.hasClass( "ui-state-disabled" ) ||
				$li.hasClass( "ui-state-processing" ) ||
				self.panels.filter( ":animated" ).length ||
				self._trigger( "select", null, self._ui( this, $show[ 0 ] ) ) === false ) {
				this.blur();
				return false;
			}

			o.selected = self.anchors.index( this );

			self.abort();

			// if tab may be closed
			if ( o.collapsible ) {
				if ( $li.hasClass( "ui-tabs-selected" ) ) {
					o.selected = -1;

					if ( o.cookie ) {
						self._cookie( o.selected, o.cookie );
					}

					self.element.queue( "tabs", function() {
						hideTab( el, $hide );
					}).dequeue( "tabs" );

					this.blur();
					return false;
				} else if ( !$hide.length ) {
					if ( o.cookie ) {
						self._cookie( o.selected, o.cookie );
					}

					self.element.queue( "tabs", function() {
						showTab( el, $show );
					});

					// TODO make passing in node possible, see also http://dev.jqueryui.com/ticket/3171
					self.load( self.anchors.index( this ) );

					this.blur();
					return false;
				}
			}

			if ( o.cookie ) {
				self._cookie( o.selected, o.cookie );
			}

			// show new tab
			if ( $show.length ) {
				if ( $hide.length ) {
					self.element.queue( "tabs", function() {
						hideTab( el, $hide );
					});
				}
				self.element.queue( "tabs", function() {
					showTab( el, $show );
				});

				self.load( self.anchors.index( this ) );
			} else {
				throw "jQuery UI Tabs: Mismatching fragment identifier.";
			}

			// Prevent IE from keeping other link focussed when using the back button
			// and remove dotted border from clicked link. This is controlled via CSS
			// in modern browsers; blur() removes focus from address bar in Firefox
			// which can become a usability and annoying problem with tabs('rotate').
			if ( $.browser.msie ) {
				this.blur();
			}
		});

		// disable click in any case
		this.anchors.bind( "click.tabs", function(){
			return false;
		});
	},

    _getIndex: function( index ) {
		// meta-function to give users option to provide a href string instead of a numerical index.
		// also sanitizes numerical indexes to valid values.
		if ( typeof index == "string" ) {
			index = this.anchors.index( this.anchors.filter( "[href$=" + index + "]" ) );
		}

		return index;
	},

	destroy: function() {
		var o = this.options;

		this.abort();

		this.element
			.unbind( ".tabs" )
			.removeClass( "ui-tabs ui-widget ui-widget-content ui-corner-all ui-tabs-collapsible" )
			.removeData( "tabs" );

		this.list.removeClass( "ui-tabs-nav ui-helper-reset ui-helper-clearfix ui-widget-header ui-corner-all" );

		this.anchors.each(function() {
			var href = $.data( this, "href.tabs" );
			if ( href ) {
				this.href = href;
			}
			var $this = $( this ).unbind( ".tabs" );
			$.each( [ "href", "load", "cache" ], function( i, prefix ) {
				$this.removeData( prefix + ".tabs" );
			});
		});

		this.lis.unbind( ".tabs" ).add( this.panels ).each(function() {
			if ( $.data( this, "destroy.tabs" ) ) {
				$( this ).remove();
			} else {
				$( this ).removeClass([
					"ui-state-default",
					"ui-corner-top",
					"ui-tabs-selected",
					"ui-state-active",
					"ui-state-hover",
					"ui-state-focus",
					"ui-state-disabled",
					"ui-tabs-panel",
					"ui-widget-content",
					"ui-corner-bottom",
					"ui-tabs-hide"
				].join( " " ) );
			}
		});

		if ( o.cookie ) {
			this._cookie( null, o.cookie );
		}

		return this;
	},

	add: function( url, label, index ) {
		if ( index === undefined ) {
			index = this.anchors.length;
		}

		var self = this,
			o = this.options,
			$li = $( o.tabTemplate.replace( /#\{href\}/g, url ).replace( /#\{label\}/g, label ) ),
			id = !url.indexOf( "#" ) ? url.replace( "#", "" ) : this._tabId( $( "a", $li )[ 0 ] );

		$li.addClass( "ui-state-default ui-corner-top" ).data( "destroy.tabs", true );

		// try to find an existing element before creating a new one
		var $panel = self.element.find( "#" + id );
		if ( !$panel.length ) {
			$panel = $( o.panelTemplate )
				.attr( "id", id )
				.data( "destroy.tabs", true );
		}
		$panel.addClass( "ui-tabs-panel ui-widget-content ui-corner-bottom ui-tabs-hide" );

		if ( index >= this.lis.length ) {
			$li.appendTo( this.list );
			$panel.appendTo( this.list[ 0 ].parentNode );
		} else {
			$li.insertBefore( this.lis[ index ] );
			$panel.insertBefore( this.panels[ index ] );
		}

		o.disabled = $.map( o.disabled, function( n, i ) {
			return n >= index ? ++n : n;
		});

		this._tabify();

		if ( this.anchors.length == 1 ) {
			o.selected = 0;
			$li.addClass( "ui-tabs-selected ui-state-active" );
			$panel.removeClass( "ui-tabs-hide" );
			this.element.queue( "tabs", function() {
				self._trigger( "show", null, self._ui( self.anchors[ 0 ], self.panels[ 0 ] ) );
			});

			this.load( 0 );
		}

		this._trigger( "add", null, this._ui( this.anchors[ index ], this.panels[ index ] ) );
		return this;
	},

	remove: function( index ) {
		index = this._getIndex( index );
		var o = this.options,
			$li = this.lis.eq( index ).remove(),
			$panel = this.panels.eq( index ).remove();

		// If selected tab was removed focus tab to the right or
		// in case the last tab was removed the tab to the left.
		if ( $li.hasClass( "ui-tabs-selected" ) && this.anchors.length > 1) {
			this.select( index + ( index + 1 < this.anchors.length ? 1 : -1 ) );
		}

		o.disabled = $.map(
			$.grep( o.disabled, function(n, i) {
				return n != index;
			}),
			function( n, i ) {
				return n >= index ? --n : n;
			});

		this._tabify();

		this._trigger( "remove", null, this._ui( $li.find( "a" )[ 0 ], $panel[ 0 ] ) );
		return this;
	},

	enable: function( index ) {
		index = this._getIndex( index );
		var o = this.options;
		if ( $.inArray( index, o.disabled ) == -1 ) {
			return;
		}

		this.lis.eq( index ).removeClass( "ui-state-disabled" );
		o.disabled = $.grep( o.disabled, function( n, i ) {
			return n != index;
		});

		this._trigger( "enable", null, this._ui( this.anchors[ index ], this.panels[ index ] ) );
		return this;
	},

	disable: function( index ) {
		index = this._getIndex( index );
		var self = this, o = this.options;
		// cannot disable already selected tab
		if ( index != o.selected ) {
			this.lis.eq( index ).addClass( "ui-state-disabled" );

			o.disabled.push( index );
			o.disabled.sort();

			this._trigger( "disable", null, this._ui( this.anchors[ index ], this.panels[ index ] ) );
		}

		return this;
	},

	select: function( index ) {
		index = this._getIndex( index );
		if ( index == -1 ) {
			if ( this.options.collapsible && this.options.selected != -1 ) {
				index = this.options.selected;
			} else {
				return this;
			}
		}
		this.anchors.eq( index ).trigger( this.options.event + ".tabs" );
		return this;
	},

	load: function( index ) {
		index = this._getIndex( index );
		var self = this,
			o = this.options,
			a = this.anchors.eq( index )[ 0 ],
			url = $.data( a, "load.tabs" );

		this.abort();

		// not remote or from cache
		if ( !url || this.element.queue( "tabs" ).length !== 0 && $.data( a, "cache.tabs" ) ) {
			this.element.dequeue( "tabs" );
			return;
		}

		// load remote from here on
		this.lis.eq( index ).addClass( "ui-state-processing" );

		if ( o.spinner ) {
			var span = $( "span", a );
			span.data( "label.tabs", span.html() ).html( o.spinner );
		}

		this.xhr = $.ajax( $.extend( {}, o.ajaxOptions, {
			url: url,
			success: function( r, s ) {
				self.element.find( self._sanitizeSelector( a.hash ) ).html( r );

				// take care of tab labels
				self._cleanup();

				if ( o.cache ) {
					$.data( a, "cache.tabs", true );
				}

				self._trigger( "load", null, self._ui( self.anchors[ index ], self.panels[ index ] ) );
				try {
					o.ajaxOptions.success( r, s );
				}
				catch ( e ) {}
			},
			error: function( xhr, s, e ) {
				// take care of tab labels
				self._cleanup();

				self._trigger( "load", null, self._ui( self.anchors[ index ], self.panels[ index ] ) );
				try {
					// Passing index avoid a race condition when this method is
					// called after the user has selected another tab.
					// Pass the anchor that initiated this request allows
					// loadError to manipulate the tab content panel via $(a.hash)
					o.ajaxOptions.error( xhr, s, index, a );
				}
				catch ( e ) {}
			}
		} ) );

		// last, so that load event is fired before show...
		self.element.dequeue( "tabs" );

		return this;
	},

	abort: function() {
		// stop possibly running animations
		this.element.queue( [] );
		this.panels.stop( false, true );

		// "tabs" queue must not contain more than two elements,
		// which are the callbacks for the latest clicked tab...
		this.element.queue( "tabs", this.element.queue( "tabs" ).splice( -2, 2 ) );

		// terminate pending requests from other tabs
		if ( this.xhr ) {
			this.xhr.abort();
			delete this.xhr;
		}

		// take care of tab labels
		this._cleanup();
		return this;
	},

	url: function( index, url ) {
		this.anchors.eq( index ).removeData( "cache.tabs" ).data( "load.tabs", url );
		return this;
	},

	length: function() {
		return this.anchors.length;
	}
});

$.extend( $.ui.tabs, {
	version: "1.8.12"
});

/*
 * Tabs Extensions
 */

/*
 * Rotate
 */
$.extend( $.ui.tabs.prototype, {
	rotation: null,
	rotate: function( ms, continuing ) {
		var self = this,
			o = this.options;

		var rotate = self._rotate || ( self._rotate = function( e ) {
			clearTimeout( self.rotation );
			self.rotation = setTimeout(function() {
				var t = o.selected;
				self.select( ++t < self.anchors.length ? t : 0 );
			}, ms );
			
			if ( e ) {
				e.stopPropagation();
			}
		});

		var stop = self._unrotate || ( self._unrotate = !continuing
			? function(e) {
				if (e.clientX) { // in case of a true click
					self.rotate(null);
				}
			}
			: function( e ) {
				t = o.selected;
				rotate();
			});

		// start rotation
		if ( ms ) {
			this.element.bind( "tabsshow", rotate );
			this.anchors.bind( o.event + ".tabs", stop );
			rotate();
		// stop rotation
		} else {
			clearTimeout( self.rotation );
			this.element.unbind( "tabsshow", rotate );
			this.anchors.unbind( o.event + ".tabs", stop );
			delete this._rotate;
			delete this._unrotate;
		}

		return this;
	}
});

})( jQuery );
/*!
 * jQuery UI AriaTabs (12.07.10)
 * http://github.com/fnagel/jQuery-Accessible-RIA
 *
 * Copyright (c) 2009 Felix Nagel for Namics (Deustchland) GmbH
 * Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
 *
 * Depends: ui.core.js 1.8
 *   		ui.tabs.js
 */ 
/* 
 USAGE:::::::::::::
* Take a look in the html file or the (german) pdf file delivered with this example
* Simply add the js file uner the regular ui.tabs.js script tag
* Supports all options, methods and callbacks of the original widget
* sortable tabs are accessable but the sortable functionality as it is provided by the ui.sortable widget doesnt support ARIA 

 * Options	
jqAddress			You need to add the add the jQuery Address file, please see demo file!
	enable			enable browser history support
	title
		enable		enable title change
		split		set delimiter string
 
*/
(function($) {
	$.fn.extend($.ui.tabs.prototype,{
	
		// when widget is initiated
		_create: function() {
			var self = this, options = this.options;	
			// add jQuery address default options
			if ($.address) {						
				var jqAddressDefOpt = { 
					enable: true,
					title: {
						enable: true,
						split: ' | '		
					}
				};			
				if (!$.isEmptyObject(options.jqAddress)) $.extend(true, jqAddressDefOpt, options.jqAddress );
				else options.jqAddress = {};
				$.extend(true, options.jqAddress, jqAddressDefOpt);
			}

			// add jQuery Address stuff
			if ($.address && options.jqAddress.enable) var anchorId = "#" + $.address.value().replace("/", '');

			// fire original function
			self._tabify(true);		
			
			// accessibility: needed to prevent blur() when enter key is pushed to enable forms mode in screenreader
			// needs to be fixed in tabs widget in line 333
			this.anchors.bind(options.event + '.tabs-accessibility', function() { this.focus(); });
			
			
			// ARIA
			// self.element.attr("role", "application");
			self.list.attr("role", "tablist");	
			for (var x = 0; x < self.anchors.length; x++) {
				// add jQuery Address stuff | get proper tab by anchor
				if ($.address && options.jqAddress.enable && anchorId != "#" && $(self.anchors[x]).attr("href") == anchorId) self.select(x);
				// init aria atrributes for each panel and anchor
				self._ariaInit(x);
			}	
			
			// keyboard
			self.list.keydown( function(event){
				switch (event.keyCode) {
					case $.ui.keyCode.RIGHT:
						self.select(options.selected+1);
						return false;
						break;
					case $.ui.keyCode.DOWN:
						self.select(options.selected+1);
						// return false;
						break;
					case $.ui.keyCode.UP:
						self.select(options.selected-1);
						return false;
						break;
					case $.ui.keyCode.LEFT:
						self.select(options.selected-1);
						return false;
						break;
					case $.ui.keyCode.END:
						self.select(self.anchors.length-1);
						return false;
						break;
					case $.ui.keyCode.HOME: 
						self.select(0);
						return false;
						break;				
				}
			});		
			
			// add jQuery address stuff
			if ($.address && this.options.jqAddress.enable) {
				$.address.externalChange(function(event) {
					// Select the proper tab
					var anchorId = "#" + event.value.replace("/", '');
					var x = 0;
					while (x < self.anchors.length) {
						if ($(self.anchors[x]).attr("href") == anchorId) {
							self.select(x); 
							return;
						}
						x++;						
					}	
				});
			}
		},
		
		_original_load: $.ui.tabs.prototype.load,
		// called whenever a tab is selected but if option collapsible is set | fired once at init for the chosen tab
		load: function(index) {	
			
			// add jQuery Address stuff
			// workaround: only set values when user interacts aka not on init
			if ($.address && this.options.jqAddress.enable) {
				if ($(this.anchors[0]).attr("aria-selected") !== undefined) {
					if (this.options.forceFirst === 0 && index !== 0) {
						// if there is no anchor to keep, prevent double entry
						if ($.address.value() == "") $.address.history(false);
						$.address.value($(this.anchors[0]).attr("href").replace(/^#/, ''));
						$.address.history(true);
						this.options.forceFirst = false;
					}
					if (this.options.jqAddress.title.enable) $.address.title($.address.title().split(this.options.jqAddress.title.split)[0] + this.options.jqAddress.title.split + $(this.anchors[index]).text());
					$.address.value($(this.anchors[index]).attr("href").replace(/^#/, ''));
				} else {
					this.options.forceFirst = index;
				}
			}
			
			// hide all unselected
			for (var x = 0; x < this.anchors.length; x++) {			
				// anchors
				this._ariaSet(x, false);
				// remove ARIA live settings
				if($.data(this.anchors[x], 'href.tabs')) {
					$(this.panels[x])
						.removeAttr("aria-live")
						.removeAttr("aria-busy");
				}
			};	
			// is remote? set ARIA states 
			if($.data(this.anchors[index], 'href.tabs')) {
				$(this.panels[index])
					.attr("aria-live", "polite")
					.attr("aria-busy", "true");
			}		
			// fire original function
			this._original_load(index);
						
			// is remote? end ARIA busy
			if($.data(this.anchors[index], 'href.tabs')) {
				$(this.panels[index])
					.attr("aria-busy", "false");				
					// TO DO jQuery Address: title is wrong when using Ajax Tab
			}			
			// set state for the activated tab
			this._ariaSet(index, true);
		},
		
		// sets aria states for single tab and its panel
		_ariaSet: function(index, state) {		
			var tabindex = (state) ? 0 : -1;
			var anchor = $(this.anchors[index]);
			// set ARIA state for loaded tab			
			anchor.attr("tabindex", tabindex)
				.attr("aria-selected", state);
			// set focus and remove focus CSS class
			if (state) {
				if (!$.browser.msie) anchor.focus(); 
			} else {
				// needed to remove CSS class set by original widget
				anchor.closest("li").removeClass("ui-state-focus");			
			}
			// set ARIA state for loaded tab
			$(this.panels[index])
				.attr("aria-hidden", !state)
				.attr("aria-expanded", state);
			// accessibility: needed to prevent blur() because IE loses focus when using keyboard control
			// this needs rto be fixed in jQuery UI Tabs in line 402
			if ($.browser.msie) this.options.timeout = window.setTimeout(function() { anchor.focus(); }, 100);
			// update virtual Buffer
			if (state) this._updateVirtualBuffer();
		},
		
		// sets all attributes when plugin is called or if tab is added
		_ariaInit: function(index) {
			var self = this;
			// get widget generated ID of the panel
			var panelId = $(this.panels[index]).attr("id");		
			// ARIA anchors and li's
			$(this.anchors[index])
				.attr("role", "tab")
				.attr("aria-controls", panelId)
				.attr("id", panelId+"-tab")
			// set li to presentation role
			.parent().attr("role", "presentation");				
			// ARIA panels aka content wrapper
			$(this.panels[index])
				.attr("role", "tabpanel")
				// add tabpanel to the tabindex
				.attr("tabindex", 0)
				.attr("aria-labelledby", panelId+"-tab");				
			// if collapsible, set event to toggle ARIA state
			if (this.options.collapsible) {
				$(this.anchors[index]).bind(this.options.event, function(event) {
					// get class to negate it to set states correctly when panel is collapsed
					self._ariaSet(index, !$(self.panels[index]).hasClass("ui-tabs-hide"));
				});
			}
		},		
		
		_original_add: $.ui.tabs.prototype.add,
		// called when a tab is added
		add: function(url, label, index) {
			// fire original function
			this._original_add(url, label, index);
			// ARIA			
			this.element
				.attr("aria-live", "polite")
				.attr("aria-relevant","additions");
			
			// if no index is defined tab should be added at the end of the tab list
			if (index) {
				this._ariaInit(index);
				this._ariaSet(index, false);
			} else {
				this._ariaInit(this.anchors.length-1);
				this._ariaSet(this.anchors.length-1, false);
			}			
		},
		
		_original_remove: $.ui.tabs.prototype.remove,
		// called when a tab is removed
		remove: function(index) {
			// fire original function
			this._original_remove(index);	
			// ARIA
			this.element
				.attr("aria-live", "polite")
				.attr("aria-relevant","removals");
		},		
		
		_original_destroy: $.ui.tabs.prototype.destroy,
		// removes all the setted attributes
		destroy: function() {
			var self = this, options = this.options;
			// remove ARIA attribute
			// wrapper element
			self.element
				.removeAttr("role")
				.removeAttr("aria-live")
				.removeAttr("aria-relevant");
			// ul element
			self.list.removeAttr("role");		
			for (var x = 0; x < self.anchors.length; x++) {
				// tabs
				$(self.anchors[x])
					.removeAttr("aria-selected")
					.removeAttr("aria-controls")
					.removeAttr("role")
					.removeAttr("id")
					.removeAttr("tabindex")
				// remove presentation role of the li element
				.parent().removeAttr("role");
				// tab panels
				$(self.panels[x])
					.removeAttr("aria-hidden")
					.removeAttr("aria-expanded")
					.removeAttr("aria-labelledby")
					.removeAttr("aria-live")
					.removeAttr("aria-busy")
					.removeAttr("aria-relevant")
					.removeAttr("role");
			}
			// remove virtual buffer form
			$("body>form #virtualBufferForm").parent().remove();
			// fire original function
			this._original_destroy();	
		},
	
		// updates virtual buffer | for older screenreader
		_updateVirtualBuffer: function() {
			var form = $("body>form #virtualBufferForm");		
			if(form.length) {
				if (form.val() == "1") form.val("0"); else  form.val("1");
				if (form.hasClass("ui-accessibility-odd")) form.addClass("ui-accessibility-even").removeClass("ui-accessibility-odd");
				else form.addClass("ui-accessibility-odd").removeClass("ui-accessibility-even");
			} else {
				$("body").append('<form><input id="virtualBufferForm" type="hidden" value="1" /></form>');
			}
		}
	});
})(jQuery); 
/*
Copyright 2011 OCAD University
Copyright 2011 Lucendo Development Ltd.

Licensed under the Educational Community License (ECL), Version 2.0 or the New
BSD license. You may not use this file except in compliance with one these
Licenses.

You may obtain a copy of the ECL 2.0 License and BSD License at
https://github.com/fluid-project/infusion/raw/master/Infusion-LICENSE.txt
*/

// Declare dependencies
/*global fluid_1_5:true, jQuery*/

// JSLint options 
/*jslint white: true, funcinvoke: true, undef: true, newcap: true, nomen: true, regexp: true, bitwise: true, browser: true, forin: true, maxerr: 100, indent: 4 */

var fluid_1_5 = fluid_1_5 || {};

(function ($, fluid) {
    /**********************
     * Tabs *
     *********************/
     
    fluid.defaults("fluid.tabs", {
        gradeNames: ["fluid.viewComponent", "autoInit"],
        tabOptions: {},
        events: { 
            // These events are forwarded out of the jQueryUI Tabs' equivalents
            // with signature (that, event, ui)
            tabsselect: "preventable",
            tabsload: null,
            tabsshow: null  
        },
        finalInitFunction: "fluid.tabs.finalInit"
    });          
    
    fluid.tabs.finalInit = function (that) {
        that.container.tabs(that.options.tabOptions);  //jQuery UI Tabs
        fluid.each(that.options.events, function(value, eventName) {
            that.container.bind(eventName, function(event, ui) {
                return that.events[eventName].fire(that, event, ui);
            });
        });
    };

})(jQuery, fluid_1_5);
/*
Copyright 2011 OCAD University
Copyright 2011 Lucendo Development Ltd.

Licensed under the Educational Community License (ECL), Version 2.0 or the New
BSD license. You may not use this file except in compliance with one these
Licenses.

You may obtain a copy of the ECL 2.0 License and BSD License at
https://github.com/fluid-project/infusion/raw/master/Infusion-LICENSE.txt
*/

// Declare dependencies
/*global fluid_1_5:true, jQuery, window */

// JSLint options 
/*jslint white: true, funcinvoke: true, undef: true, newcap: true, nomen: true, regexp: true, bitwise: true, browser: true, forin: true, maxerr: 100, indent: 4 */

var fluid_1_5 = fluid_1_5 || {};

(function ($, fluid) {
    
    /******
    * ToC *
    *******/
    fluid.registerNamespace("fluid.tableOfContents");


    
    fluid.tableOfContents.insertAnchor = function (name, element) {
       // In order to resolve FLUID-4453, we need to make sure that the owner document is correctly
       // taken from the target element (the preview may be in an iframe)
        var anchor = $("<a></a>", element.ownerDocument);
        anchor.prop({
            name: name,
            id: name
        });
        anchor.insertBefore(element);
    };
    
    fluid.tableOfContents.generateGUID = function () {
        return fluid.allocateSimpleId();
    };
       
    /**
     * Invoker function to filter headings.  Default is to filter out the visible headings.
     * @param   Object  Contains a list of headings, usually generated by that.locate("headings")
     * @return  filtered headings
     */
    fluid.tableOfContents.filterHeadings = function (headings) {
        return headings.filter(":visible");
    };
    
    fluid.tableOfContents.finalInit = function (that) {
        var headings = that.filterHeadings(that.locate("headings"));
        
        that.headingTextToAnchor = function (heading) {
            var guid = that.generateGUID();
            
            var anchorInfo = {
                id: guid,
                url: "#" + guid
            };
            
            that.insertAnchor(anchorInfo.id, heading);
            return anchorInfo;
        };
        
        that.anchorInfo = fluid.transform(headings, function (heading) {
            return that.headingTextToAnchor(heading);
        });
        
        // TODO: is it weird to have hide and show on a component?
        that.hide = function () {
            that.locate("tocContainer").hide();
        };
        
        that.show = function () {
            that.locate("tocContainer").show();
        };
        
        that.model = that.modelBuilder.assembleModel(headings, that.anchorInfo);

        that.events.onReady.fire();
    };
    
    
    fluid.defaults("fluid.tableOfContents", {
        gradeNames: ["fluid.viewComponent", "autoInit"],
        finalInitFunction: "fluid.tableOfContents.finalInit",
        components: {
            levels: {
                type: "fluid.tableOfContents.levels",
                container: "{tableOfContents}.dom.tocContainer",
                createOnEvent: "onReady",
                options: {
                    model: {
                        headings: "{tableOfContents}.model"
                    }, 
                    events: {
                        afterRender: "{tableOfContents}.events.afterRender"
                    }
                }
            },
            modelBuilder: {
                type: "fluid.tableOfContents.modelBuilder"
            }
        },
        invokers: {
            insertAnchor: "fluid.tableOfContents.insertAnchor",
            generateGUID: "fluid.tableOfContents.generateGUID",
            filterHeadings: "fluid.tableOfContents.filterHeadings"
        },
        selectors: {
            headings: ":header",
            tocContainer: ".flc-toc-tocContainer"
        },
        events: {
            onReady: null,
            afterRender: null
        }
    });
    
    
    /*******************
    * ToC ModelBuilder *
    ********************/
    fluid.registerNamespace("fluid.tableOfContents.modelBuilder");
    
    fluid.tableOfContents.modelBuilder.toModel = function (headingInfo, modelLevelFn) {
        var headings = fluid.copy(headingInfo);
        var buildModelLevel = function (headings, level) {
            var modelLevel = [];
            while (headings.length > 0) {
                var heading = headings[0];
                if (heading.level < level) {
                    break;
                }
                if (heading.level > level) {
                    var subHeadings = buildModelLevel(headings, level + 1);
                    if (modelLevel.length > 0) {
                        modelLevel[modelLevel.length - 1].headings = subHeadings;
                    } else {
                        modelLevel = modelLevelFn(modelLevel, subHeadings);
                    }
                }
                if (heading.level === level) {
                    modelLevel.push(heading); 
                    headings.shift();
                }
            }
            return modelLevel;
        };
        return buildModelLevel(headings, 1);
    };
       
    fluid.tableOfContents.modelBuilder.gradualModelLevelFn = function (modelLevel, subHeadings) {
        // Clone the subHeadings because we don't want to modify the reference of the subHeadings.  
        // the reference will affect the equality condition in generateTree(), resulting an unwanted tree.
        var subHeadingsClone = fluid.copy(subHeadings);
        subHeadingsClone[0].level--;
        return subHeadingsClone;
    };

    fluid.tableOfContents.modelBuilder.skippedModelLevelFn = function (modelLevel, subHeadings) {
        modelLevel.push({headings: subHeadings});
        return modelLevel;
    };
    
    fluid.tableOfContents.modelBuilder.finalInit = function (that) {
        
        that.convertToHeadingObjects = function (headings, anchorInfo) {
            headings = $(headings);
            return fluid.transform(headings, function (heading, index) {
                return {
                    level: that.headingCalculator.getHeadingLevel(heading),
                    text: $(heading).text(),
                    url: anchorInfo[index].url
                };
            });
        };
        
        that.assembleModel = function (headings, anchorInfo) {
            var headingInfo = that.convertToHeadingObjects(headings, anchorInfo);
            return that.toModel(headingInfo);
        };
    };
    
    fluid.defaults("fluid.tableOfContents.modelBuilder", {
        gradeNames: ["fluid.littleComponent", "autoInit"],
        finalInitFunction: "fluid.tableOfContents.modelBuilder.finalInit",
        components: {
            headingCalculator: {
                type: "fluid.tableOfContents.modelBuilder.headingCalculator"
            }
        },
        invokers: {
            toModel: {
                funcName: "fluid.tableOfContents.modelBuilder.toModel",
                args: ["{arguments}.0", "{modelBuilder}.modelLevelFn"]
            },
            modelLevelFn: "fluid.tableOfContents.modelBuilder.gradualModelLevelFn"
        }
    });
    
    /*************************************
    * ToC ModelBuilder headingCalculator *
    **************************************/
    fluid.registerNamespace("fluid.tableOfContents.modelBuilder.headingCalculator");
    
    fluid.tableOfContents.modelBuilder.headingCalculator.finalInit = function (that) {
        that.getHeadingLevel = function (heading) {
            return $.inArray(heading.tagName, that.options.levels) + 1;
        };
    };
    
    fluid.defaults("fluid.tableOfContents.modelBuilder.headingCalculator", {
        gradeNames: ["fluid.littleComponent", "autoInit"],
        finalInitFunction: "fluid.tableOfContents.modelBuilder.headingCalculator.finalInit",
        levels: ["H1", "H2", "H3", "H4", "H5", "H6"]
    });
    
    /*************
    * ToC Levels *
    **************/
    fluid.registerNamespace("fluid.tableOfContents.levels");
    
    fluid.tableOfContents.levels.finalInit = function (that) {
        fluid.fetchResources(that.options.resources, function () {
            that.container.append(that.options.resources.template.resourceText);
            that.refreshView();
        });        
    };

    /**
     * Create an object model based on the type and ID.  The object should contain an
     * ID that maps the selectors (ie. level1:), and the object should contain a children
     * @param   string      Accepted values are: level, items
     * @param   int         The current level which is used here as the ID.
     */
    fluid.tableOfContents.levels.objModel = function (type, ID) {
        var objModel = {
            ID: type + ID + ":",
            children: []
        };
        return objModel;
    };
    
    /** 
     * Configure item object when item object has no text, uri, level in it.
     * defaults to add a decorator to hide the bullets.
     */
    fluid.tableOfContents.levels.handleEmptyItemObj = function (itemObj) {
        itemObj.decorators = [{
            type: "addClass",
            classes: "fl-tableOfContents-hide-bullet"
        }];
    };
    
    /**
     * @param   Object  that.model, the model with all the headings, it should be in the format of {headings: [...]}
     * @param   int     the current level we want to generate the tree for.  default to 1 if not defined.
     * @return  Object  A tree that looks like {children: [{ID: x, subTree:[...]}, ...]}
     */
    fluid.tableOfContents.levels.generateTree = function (headingsModel, currentLevel) {
        currentLevel = currentLevel || 0;
        var levelObj = fluid.tableOfContents.levels.objModel("level", currentLevel);
        
        // FLUID-4352, run generateTree iff there are headings in the model.
        if (headingsModel.headings.length === 0) {
            return [];
        }
        
        // base case: level is 0, returns {children:[generateTree(nextLevel)]}
        // purpose is to wrap the first level with a children object.
        if (currentLevel === 0) {
            var tree = {
                children: [
                    fluid.tableOfContents.levels.generateTree(headingsModel, currentLevel + 1)
                ]
            };
            return tree;
        }
        
        // Loop through the heading array, which can have multiple headings on the same level
        $.each(headingsModel.headings, function (index, model) {
            var itemObj = fluid.tableOfContents.levels.objModel("items", currentLevel);
            var linkObj = {
                ID: "link" + currentLevel,
                target: model.url,
                linktext: model.text
            };
            
            // If level is undefined, then add decorator to it, otherwise add the links to it.
            if (!model.level) {
                fluid.tableOfContents.levels.handleEmptyItemObj(itemObj);
            } else {
                itemObj.children.push(linkObj);
            }
            // If there are sub-headings, go into the next level recursively
            if (model.headings) {
                itemObj.children.push(fluid.tableOfContents.levels.generateTree(model, currentLevel + 1));
            }
            // At this point, the itemObj should be in a tree format with sub-headings children
            levelObj.children.push(itemObj);
        });
        return levelObj;
    };
    
    /** 
     * @return  Object  Returned produceTree must be in {headings: [trees]}
     */
    fluid.tableOfContents.levels.produceTree = function (that) {
        return fluid.tableOfContents.levels.generateTree(that.model);
    };
     
    fluid.defaults("fluid.tableOfContents.levels", {
        gradeNames: ["fluid.rendererComponent", "autoInit"],
        finalInitFunction: "fluid.tableOfContents.levels.finalInit",
        produceTree: "fluid.tableOfContents.levels.produceTree",
        selectors: {
            level1: ".flc-toc-levels-level1",
            level2: ".flc-toc-levels-level2",
            level3: ".flc-toc-levels-level3",
            level4: ".flc-toc-levels-level4",
            level5: ".flc-toc-levels-level5",
            level6: ".flc-toc-levels-level6",
            items1: ".flc-toc-levels-items1",
            items2: ".flc-toc-levels-items2",
            items3: ".flc-toc-levels-items3",
            items4: ".flc-toc-levels-items4",
            items5: ".flc-toc-levels-items5",
            items6: ".flc-toc-levels-items6",
            link1: ".flc-toc-levels-link1",
            link2: ".flc-toc-levels-link2",
            link3: ".flc-toc-levels-link3",
            link4: ".flc-toc-levels-link4",
            link5: ".flc-toc-levels-link5",
            link6: ".flc-toc-levels-link6"            
        },
        repeatingSelectors: ["level1", "level2", "level3", "level4", "level5", "level6", "items1", "items2", "items3", "items4", "items5", "items6"],
        model: {
            headings: [] // [text: heading, url: linkURL, headings: [ an array of subheadings in the same format]
        },
        resources: {
            template: {
                forceCache: true,
                url: "../html/TableOfContents.html"
            }
        }, 
        rendererFnOptions: {
            noexpand: true
        },
        rendererOptions: {
            debugMode: false
        }

    });

})(jQuery, fluid_1_5);
/*
    json2.js
    2007-11-06

    Public Domain

    No warranty expressed or implied. Use at your own risk.

    See http://www.JSON.org/js.html

    This file creates a global JSON object containing two methods:

        JSON.stringify(value, whitelist)
            value       any JavaScript value, usually an object or array.

            whitelist   an optional that determines how object values are
                        stringified.

            This method produces a JSON text from a JavaScript value.
            There are three possible ways to stringify an object, depending
            on the optional whitelist parameter.

            If an object has a toJSON method, then the toJSON() method will be
            called. The value returned from the toJSON method will be
            stringified.

            Otherwise, if the optional whitelist parameter is an array, then
            the elements of the array will be used to select members of the
            object for stringification.

            Otherwise, if there is no whitelist parameter, then all of the
            members of the object will be stringified.

            Values that do not have JSON representaions, such as undefined or
            functions, will not be serialized. Such values in objects will be
            dropped, in arrays will be replaced with null. JSON.stringify()
            returns undefined. Dates will be stringified as quoted ISO dates.

            Example:

            var text = JSON.stringify(['e', {pluribus: 'unum'}]);
            // text is '["e",{"pluribus":"unum"}]'

        JSON.parse(text, filter)
            This method parses a JSON text to produce an object or
            array. It can throw a SyntaxError exception.

            The optional filter parameter is a function that can filter and
            transform the results. It receives each of the keys and values, and
            its return value is used instead of the original value. If it
            returns what it received, then structure is not modified. If it
            returns undefined then the member is deleted.

            Example:

            // Parse the text. If a key contains the string 'date' then
            // convert the value to a date.

            myData = JSON.parse(text, function (key, value) {
                return key.indexOf('date') >= 0 ? new Date(value) : value;
            });

    This is a reference implementation. You are free to copy, modify, or
    redistribute.

    Use your own copy. It is extremely unwise to load third party
    code into your pages.
*/

/*jslint evil: true */
/*extern JSON */

if (!this.JSON) {

    JSON = function () {

        function f(n) {    // Format integers to have at least two digits.
            return n < 10 ? '0' + n : n;
        }

        Date.prototype.toJSON = function () {

// Eventually, this method will be based on the date.toISOString method.

            return this.getUTCFullYear()   + '-' +
                 f(this.getUTCMonth() + 1) + '-' +
                 f(this.getUTCDate())      + 'T' +
                 f(this.getUTCHours())     + ':' +
                 f(this.getUTCMinutes())   + ':' +
                 f(this.getUTCSeconds())   + 'Z';
        };


        var m = {    // table of character substitutions
            '\b': '\\b',
            '\t': '\\t',
            '\n': '\\n',
            '\f': '\\f',
            '\r': '\\r',
            '"' : '\\"',
            '\\': '\\\\'
        };

        function stringify(value, whitelist) {
            var a,          // The array holding the partial texts.
                i,          // The loop counter.
                k,          // The member key.
                l,          // Length.
                r = /["\\\x00-\x1f\x7f-\x9f]/g,
                v;          // The member value.

            switch (typeof value) {
            case 'string':

// If the string contains no control characters, no quote characters, and no
// backslash characters, then we can safely slap some quotes around it.
// Otherwise we must also replace the offending characters with safe sequences.

                return r.test(value) ?
                    '"' + value.replace(r, function (a) {
                        var c = m[a];
                        if (c) {
                            return c;
                        }
                        c = a.charCodeAt();
                        return '\\u00' + Math.floor(c / 16).toString(16) +
                                                   (c % 16).toString(16);
                    }) + '"' :
                    '"' + value + '"';

            case 'number':

// JSON numbers must be finite. Encode non-finite numbers as null.

                return isFinite(value) ? String(value) : 'null';

            case 'boolean':
            case 'null':
                return String(value);

            case 'object':

// Due to a specification blunder in ECMAScript,
// typeof null is 'object', so watch out for that case.

                if (!value) {
                    return 'null';
                }

// If the object has a toJSON method, call it, and stringify the result.

                if (typeof value.toJSON === 'function') {
                    return stringify(value.toJSON());
                }
                a = [];
                if (typeof value.length === 'number' &&
                        !(value.propertyIsEnumerable('length'))) {

// The object is an array. Stringify every element. Use null as a placeholder
// for non-JSON values.

                    l = value.length;
                    for (i = 0; i < l; i += 1) {
                        a.push(stringify(value[i], whitelist) || 'null');
                    }

// Join all of the elements together and wrap them in brackets.

                    return '[' + a.join(',') + ']';
                }
                if (whitelist) {

// If a whitelist (array of keys) is provided, use it to select the components
// of the object.

                    l = whitelist.length;
                    for (i = 0; i < l; i += 1) {
                        k = whitelist[i];
                        if (typeof k === 'string') {
                            v = stringify(value[k], whitelist);
                            if (v) {
                                a.push(stringify(k) + ':' + v);
                            }
                        }
                    }
                } else {

// Otherwise, iterate through all of the keys in the object.

                    for (k in value) {
                        if (typeof k === 'string') {
                            v = stringify(value[k], whitelist);
                            if (v) {
                                a.push(stringify(k) + ':' + v);
                            }
                        }
                    }
                }

// Join all of the member texts together and wrap them in braces.

                return '{' + a.join(',') + '}';
            }
        }

        return {
            stringify: stringify,
            parse: function (text, filter) {
                var j;

                function walk(k, v) {
                    var i, n;
                    if (v && typeof v === 'object') {
                        for (i in v) {
                            if (Object.prototype.hasOwnProperty.apply(v, [i])) {
                                n = walk(i, v[i]);
                                if (n !== undefined) {
                                    v[i] = n;
                                }
                            }
                        }
                    }
                    return filter(k, v);
                }


// Parsing happens in three stages. In the first stage, we run the text against
// regular expressions that look for non-JSON patterns. We are especially
// concerned with '()' and 'new' because they can cause invocation, and '='
// because it can cause mutation. But just to be safe, we want to reject all
// unexpected forms.

// We split the first stage into 4 regexp operations in order to work around
// crippling inefficiencies in IE's and Safari's regexp engines. First we
// replace all backslash pairs with '@' (a non-JSON character). Second, we
// replace all simple value tokens with ']' characters. Third, we delete all
// open brackets that follow a colon or comma or that begin the text. Finally,
// we look to see that the remaining characters are only whitespace or ']' or
// ',' or ':' or '{' or '}'. If that is so, then the text is safe for eval.

                if (/^[\],:{}\s]*$/.test(text.replace(/\\./g, '@').
replace(/"[^"\\\n\r]*"|true|false|null|-?\d+(?:\.\d*)?(:?[eE][+\-]?\d+)?/g, ']').
replace(/(?:^|:|,)(?:\s*\[)+/g, ''))) {

// In the second stage we use the eval function to compile the text into a
// JavaScript structure. The '{' operator is subject to a syntactic ambiguity
// in JavaScript: it can begin a block or an object literal. We wrap the text
// in parens to eliminate the ambiguity.

                    j = eval('(' + text + ')');

// In the optional third stage, we recursively walk the new structure, passing
// each name/value pair to a filter function for possible transformation.

                    return typeof filter === 'function' ? walk('', j) : j;
                }

// If the text is not JSON parseable, then a SyntaxError is thrown.

                throw new SyntaxError('parseJSON');
            }
        };
    }();
}
/*
Copyright 2009-2010 University of Cambridge
Copyright 2011 Lucendo Development Ltd.

Licensed under the Educational Community License (ECL), Version 2.0 or the New
BSD license. You may not use this file except in compliance with one these
Licenses.

You may obtain a copy of the ECL 2.0 License and BSD License at
https://github.com/fluid-project/infusion/raw/master/Infusion-LICENSE.txt
*/

// Declare dependencies
/*global fluid_1_5:true, jQuery*/

// JSLint options 
/*jslint white: true, funcinvoke: true, undef: true, newcap: true, nomen: true, regexp: true, bitwise: true, browser: true, forin: true, maxerr: 100, indent: 4 */

var fluid_1_5 = fluid_1_5 || {};

(function ($, fluid) {

    /** URL utilities salvaged from kettle - these should go into core framework **/
  
    fluid.generate = function (n, generator) {
        var togo = [];
        for (var i = 0; i < n; ++ i) {
            togo[i] = typeof(generator) === "function" ?
                generator.call(null, i) : generator;
        }
        return togo;       
    };

    fluid.registerNamespace("fluid.url");
   
    fluid.url.generateDepth = function(depth) {
        return fluid.generate(depth, "../").join("");
    };
   
    fluid.url.parsePathInfo = function (pathInfo) {
        var togo = {};
        var segs = pathInfo.split("/");
        if (segs.length > 0) {
            var top = segs.length - 1;
            var dotpos = segs[top].indexOf(".");
            if (dotpos !== -1) {
                togo.extension = segs[top].substring(dotpos + 1);
                segs[top] = segs[top].substring(0, dotpos);
            }
        }
        togo.pathInfo = segs;
        return togo;
    };
    
    fluid.url.parsePathInfoTrim = function (pathInfo) {
        var togo = fluid.url.parsePathInfo(pathInfo);
        if (togo.pathInfo[togo.pathInfo.length - 1] === "") {
            togo.pathInfo.length--;
        }
        return togo;
    };
    
    /** Collapse the array of segments into a URL path, starting at the specified
     * segment index - this will not terminate with a slash, unless the final segment
     * is the empty string
     */
    fluid.url.collapseSegs = function(segs, from, to) {
        var togo = "";
        if (from === undefined) { 
            from = 0;
        }
        if (to === undefined) {
            to = segs.length;
        }
        for (var i = from; i < to - 1; ++ i) {
            togo += segs[i] + "/";
        }
        if (to > from) { // TODO: bug in Kettle version
            togo += segs[to - 1];
        }
        return togo;   
    };
    
    fluid.url.makeRelPath = function(parsed, index) {
        var togo = fluid.kettle.collapseSegs(parsed.pathInfo, index);
        if (parsed.extension) {
            togo += "." + parsed.extension;
        }
        return togo;
    };
    
    /** Canonicalise IN PLACE the supplied segment array derived from parsing a
     * pathInfo structure. Warning, this destructively modifies the argument.
     */
    fluid.url.cononocolosePath = function(pathInfo) {
        var consume = 0;
        for (var i = 0; i < pathInfo.length; ++ i) {
            if (pathInfo[i] === "..") {
                ++consume;
            }
            else if (consume !== 0) {
                pathInfo.splice(i - consume*2, consume*2);
                i -= consume * 2;
                consume = 0;
            }
        }
        return pathInfo;
    };
    
    // parseUri 1.2.2
    // (c) Steven Levithan <stevenlevithan.com>
    // MIT License
    
    fluid.url.parseUri = function (str) {
        var o  = fluid.url.parseUri.options,
          m   = o.parser[o.strictMode ? "strict" : "loose"].exec(str),
          uri = {},
          i   = 14;
      
        while (i--) uri[o.key[i]] = m[i] || "";
      
        uri[o.q.name] = {};
        uri[o.key[12]].replace(o.q.parser, function ($0, $1, $2) {
            if ($1) uri[o.q.name][$1] = $2;
        });
      
        return uri;
    };
    
    fluid.url.parseUri.options = {
        strictMode: true,
        key: ["source","protocol","authority","userInfo","user","password","host","port","relative","path","directory","file","query","anchor"],
        q:   {
            name:   "queryKey",
            parser: /(?:^|&)([^&=]*)=?([^&]*)/g
        },
        parser: {
            strict: /^(?:([^:\/?#]+):)?(?:\/\/((?:(([^:@]*)(?::([^:@]*))?)?@)?([^:\/?#]*)(?::(\d*))?))?((((?:[^?#\/]*\/)*)([^?#]*))(?:\?([^#]*))?(?:#(.*))?)/,
            loose:  /^(?:(?![^:@]+:[^:@\/]*@)([^:\/?#.]+):)?(?:\/\/)?((?:(([^:@]*)(?::([^:@]*))?)?@)?([^:\/?#]*)(?::(\d*))?)(((\/(?:[^?#](?![^?#\/]*\.[^?#\/.]+(?:[?#]|$)))*\/?)?([^?#\/]*))(?:\?([^#]*))?(?:#(.*))?)/
        }
    };
    
    fluid.url.parseSegs = function(url) {
        var parsed = fluid.url.parseUri(url);
        var parsedSegs = fluid.url.parsePathInfoTrim(parsed.directory);
        return parsedSegs.pathInfo;
    };
    
    fluid.url.isAbsoluteUrl = function(url) {
        var parseRel = fluid.url.parseUri(url);
        return (parseRel.host || parseRel.protocol || parseRel.directory.charAt(0) === '/');
    };
    
    fluid.url.computeRelativePrefix = function(outerLocation, iframeLocation, relPath) {
        if (fluid.url.isAbsoluteUrl(relPath)) {
            return relPath;
        }
        var relSegs = fluid.url.parsePathInfo(relPath).pathInfo;
        var parsedOuter = fluid.url.parseSegs(outerLocation);
        var parsedRel = parsedOuter.concat(relSegs);
        fluid.url.cononocolosePath(parsedRel);
        var parsedInner = fluid.url.parseSegs(iframeLocation);
        var seg = 0;
        for (; seg < parsedRel.length; ++ seg) {
            if (parsedRel[seg] != parsedInner[seg]) break;  
        }
        var excess = parsedInner.length - seg;
        var back = fluid.url.generateDepth(excess);
        var front = fluid.url.collapseSegs(parsedRel, seg);
        return back + front;
    };
    
})(jQuery, fluid_1_5);/*
Copyright 2009 University of Toronto
Copyright 2011 OCAD University

Licensed under the Educational Community License (ECL), Version 2.0 or the New
BSD license. You may not use this file except in compliance with one these
Licenses.

You may obtain a copy of the ECL 2.0 License and BSD License at
https://github.com/fluid-project/infusion/raw/master/Infusion-LICENSE.txt
*/

// Declare dependencies
/*global fluid_1_5:true, jQuery*/

// JSLint options 
/*jslint white: true, funcinvoke: true, undef: true, newcap: true, nomen: true, regexp: true, bitwise: true, browser: true, forin: true, maxerr: 100, indent: 4 */

var fluid_1_5 = fluid_1_5 || {};

(function ($, fluid) {
    
    fluid.defaults("fluid.uiOptions.store", {
        gradeNames: ["fluid.littleComponent", "autoInit"],
        defaultSiteSettings: {
            textFont: "default",          // key from classname map
            theme: "default",             // key from classname map
            textSize: 1,                  // in points
            lineSpacing: 1,               // in ems
            layout: false,                // boolean
            toc: false,                   // boolean
            links: false,                 // boolean
            inputsLarger: false,          // boolean
            captions: false,              // boolean
            transcripts: false,           // boolean
            language: "en",               // ISO 639-1 language code
            volume: 50                    // number between 0 and 100
        }
    });
    
    /****************
     * Cookie Store *
     ****************/
     
    /**
     * SettingsStore Subcomponent that uses a cookie for persistence.
     * @param {Object} options
     */
    fluid.defaults("fluid.cookieStore", {
        gradeNames: ["fluid.uiOptions.store", "autoInit"],
        invokers: {
            fetch: {
                funcName: "fluid.cookieStore.fetch",
                args: ["{cookieStore}.options.cookie.name", "{cookieStore}.options.defaultSiteSettings"]
            },
            save: {
                funcName: "fluid.cookieStore.save",
                args: ["{arguments}.0", "{cookieStore}.options.cookie"]
            }
        },
        cookie: {
            name: "fluid-ui-settings",
            path: "/",
            expires: ""
        }
    });

    /**
     * Retrieve and return the value of the cookie
     */
    fluid.cookieStore.fetch = function (cookieName, defaults) {
        var cookie = document.cookie;
        var cookiePrefix = cookieName + "=";
        var retObj, startIndex, endIndex;
        
        if (cookie.length > 0) {
            startIndex = cookie.indexOf(cookiePrefix);
            if (startIndex > -1) { 
                startIndex = startIndex + cookiePrefix.length; 
                endIndex = cookie.indexOf(";", startIndex);
                if (endIndex < startIndex) {
                    endIndex = cookie.length;
                }
                retObj = JSON.parse(decodeURIComponent(cookie.substring(startIndex, endIndex)));
            } 
        }
        
        return $.extend(true, {}, defaults, retObj);
    };
    
    /**
     * Assembles the cookie string
     * @param {Object} cookie settings
     */
    fluid.cookieStore.assembleCookie = function (cookieOptions) {
        var cookieStr = cookieOptions.name + "=" + cookieOptions.data;
        
        if (cookieOptions.expires) {
            cookieStr += "; expires=" + cookieOptions.expires;
        }
        
        if (cookieOptions.path) {
            cookieStr += "; path=" + cookieOptions.path;
        }
        
        return cookieStr;
    };

    /**
     * Saves the settings into a cookie
     * @param {Object} settings
     * @param {Object} cookieOptions
     */
    fluid.cookieStore.save = function (settings, cookieOptions) {
        cookieOptions.data = encodeURIComponent(JSON.stringify(settings));
        document.cookie = fluid.cookieStore.assembleCookie(cookieOptions);
    };
    

    /**************
     * Temp Store *
     **************/

    /**
     * SettingsStore Subcomponent that doesn't do persistence.
     * @param {Object} options
     */
    fluid.defaults("fluid.tempStore", {
        gradeNames: ["fluid.uiOptions.store", "autoInit"],
        invokers: {
            fetch: {
                funcName: "fluid.tempStore.fetch",
                args: ["{tempStore}"]
            },
            save: {
                funcName: "fluid.tempStore.save",
                args: ["{arguments}.0", "{tempStore}"]
            }
        },
        finalInitFunction: "fluid.tempStore.finalInit"
    });

    fluid.tempStore.finalInit = function (that) {
        that.model = that.options.defaultSiteSettings;
    };
    
    fluid.tempStore.fetch = function (that) {
        return that.model;
    };

    fluid.tempStore.save = function (settings, that) {
        that.model = settings;
    };

})(jQuery, fluid_1_5);/*
Copyright 2009 University of Toronto
Copyright 2010-2011 OCAD University
Copyright 2011 Lucendo Development Ltd.

Licensed under the Educational Community License (ECL), Version 2.0 or the New
BSD license. You may not use this file except in compliance with one these
Licenses.

You may obtain a copy of the ECL 2.0 License and BSD License at
https://github.com/fluid-project/infusion/raw/master/Infusion-LICENSE.txt
*/

// Declare dependencies
/*global fluid_1_5:true, jQuery*/

// JSLint options 
/*jslint white: true, funcinvoke: true, undef: true, newcap: true, nomen: true, regexp: true, bitwise: true, browser: true, forin: true, maxerr: 100, indent: 4 */

var fluid_1_5 = fluid_1_5 || {};

(function ($, fluid) {

    /*******************************************************************************
     * Browser type and version detection.                                         *
     *                                                                             *
     * Add type tags of IE and browser version into static environment for the     * 
     * spcial handling on IE6.                                                     *
     *******************************************************************************/
    
    fluid.registerNamespace("fluid.browser.version");

    fluid.browser.msie = function () {
        var isIE = ($.browser.msie);
        return isIE ? fluid.typeTag("fluid.browser.msie") : undefined;
    };

    fluid.browser.majorVersion = function () {
    // From http://www.useragentstring.com/pages/Internet%20Explorer/ several variants are possible
    // for IE6 - and in general we probably just want to detect major versions
        var version = $.browser.version;
        var dotpos = version.indexOf(".");
        var majorVersion = version.substring(0, dotpos);
        return fluid.typeTag("fluid.browser.majorVersion." + majorVersion);
    };

    var features = {
        browserIE: fluid.browser.msie(),
        browserMajorVersion: fluid.browser.majorVersion()
    };
    
    fluid.merge(null, fluid.staticEnvironment, features);
    
    // Temporary solution pending revised IoC system in 1.5
    
    fluid.hasFeature = function (tagName) {
        return fluid.find(fluid.staticEnvironment, function (value) {
            return value && value.typeName === tagName ? true : undefined;
        });
    };

    /*******************************************************************************
     * UI Enhancer                                                                 *
     *                                                                             *
     * Works in conjunction with FSS to transform the page based on user settings. *
     *******************************************************************************/
    
    fluid.defaults("fluid.uiEnhancer", {
        gradeNames: ["fluid.viewComponent", "autoInit"],
        components: {
            textSize: {
                type: "fluid.uiEnhancer.textSizer",
                container: "{uiEnhancer}.container",
                options: {
                    invokers: {
                        calcInitSize: {
                            funcName: "fluid.uiEnhancer.textSizer.calcInitSize",
                            args: ["{textSizer}.container", "{uiEnhancer}.options.fontSizeMap"]
                        }
                    }
                }
            },
            tableOfContents: {
                type: "fluid.tableOfContents",
                container: "{uiEnhancer}.container",
                createOnEvent: "onCreateTOCReady",
                options: {
                    components: {
                        levels: {
                            type: "fluid.tableOfContents.levels",
                            options: {
                                resources: {
                                    template: {
                                        forceCache: true,
                                        url: "{uiEnhancer}.options.tocTemplate"
                                    }
                                }
                            } 
                        }
                    },
                    listeners: {
                      // TODO: This is as a result of lack of FLUID-4398, event relay
                        afterRender: "{uiEnhancer}.lateRefreshRelay"
                    }
                }
            },
            textFont: {
                type: "fluid.uiEnhancer.classSwapper",
                container: "{uiEnhancer}.container",
                options: {
                    classes: "{uiEnhancer}.options.classnameMap.textFont"
                }
            },
            lineSpacing: {
                type: "fluid.uiEnhancer.lineSpacer",
                container: "{uiEnhancer}.container",
                options: {
                    invokers: {
                        calcInitSize: {
                            funcName: "fluid.uiEnhancer.lineSpacer.calcInitSize",
                            args: ["{lineSpacer}.container", "{uiEnhancer}.options.fontSizeMap"]
                        }
                    }
                }
            },
            theme: {
                type: "fluid.uiEnhancer.classSwapper",
                container: "{uiEnhancer}.container",
                options: {
                    classes: "{uiEnhancer}.options.classnameMap.theme"
                }
            },
            settingsStore: {
                type: "fluid.uiOptions.store",
                options: {
                    defaultSiteSettings: "{uiEnhancer}.options.defaultSiteSettings"
                }
            }
        },
        invokers: {
            updateModel: {
                funcName: "fluid.uiEnhancer.updateModel",
                args: ["@0", "{uiEnhancer}.applier"]
            },
            updateFromSettingsStore: {
                funcName: "fluid.uiEnhancer.updateFromSettingsStore",
                args: ["{uiEnhancer}"]
            },
            refreshView: {
                funcName: "fluid.uiEnhancer.refreshView",
                args: ["{uiEnhancer}"]
            },
            styleElements: "fluid.uiEnhancer.styleElements",
            
            // NOTE: when we do the ants refactoring each of these will be half an ant
            setLayout: "fluid.uiEnhancer.setLayout",
            styleLinks: "fluid.uiEnhancer.styleLinks",
            styleInputs: "fluid.uiEnhancer.styleInputs",
            setIE6ColorInversion: "fluid.uiEnhancer.setIE6ColorInversion"
        },
        events: {
            onCreateTOCReady: null,
            lateRefreshView: null,
            modelChanged: null
        },
        listeners: {
            "lateRefreshView.domReading": "fluid.uiEnhancer.applyDomReadingSettings"
        },
        classnameMap: {
            "textFont": {
                "default": "",
                "times": "fl-font-uio-times",
                "comic": "fl-font-uio-comic-sans",
                "arial": "fl-font-uio-arial",
                "verdana": "fl-font-uio-verdana"
            },
            "theme": {
                "default": "fl-uio-default-theme",
                "bw": "fl-theme-uio-bw fl-theme-bw",
                "wb": "fl-theme-uio-wb fl-theme-wb",
                "by": "fl-theme-uio-by fl-theme-by",
                "yb": "fl-theme-uio-yb fl-theme-yb"
            },
            "layout": "fl-layout-linear",
            "links": "fl-text-underline fl-text-bold fl-text-larger", 
            "inputsLarger": "fl-text-larger"
        },
        fontSizeMap: {
            "xx-small": "9px",
            "x-small":  "11px",
            "small":    "13px",
            "medium":   "15px",
            "large":    "18px",
            "x-large":  "23px",
            "xx-large": "30px"
        },
        selectors: {
            colorInversion: ".fl-inverted-color"
        },
        styles: {
            colorInversionClass: "fl-inverted-color"
        },
        finalInitFunction: "fluid.uiEnhancer.finalInit"
    });

    fluid.uiEnhancer.finalInit = function (that) {
        that.applier.modelChanged.addListener("",
            function (newModel, oldModel, changeRequest) {
                that.events.modelChanged.fire(newModel, oldModel, changeRequest);
                that.refreshView();   
            });

        that.lateRefreshRelay = function () {
            that.events.lateRefreshView.fire(that);
        };
        that.updateFromSettingsStore();
        return that;
    };
    
    fluid.uiEnhancer.updateFromSettingsStore = function (that) {
        that.updateModel(that.settingsStore.fetch());
    };

    fluid.uiEnhancer.updateModel = function (newModel, applier) {
        applier.requestChange("", newModel);
    };

    fluid.uiEnhancer.applyTocSetting = function (that) {
        var async = false;
        if (that.model.toc) {
            if (that.tableOfContents) {
                that.tableOfContents.show();
            } else {
                that.events.onCreateTOCReady.fire();
                async = true;
            }
        } else {
            if (that.tableOfContents) {
                that.tableOfContents.hide();
            }
        }
        if (!async) {
            that.lateRefreshRelay();
        }
    };

    // Apply those UIEnhancer settings which require reading elements from the DOM - 
    // as opposed to those which may be honoured by static CSS styles
    fluid.uiEnhancer.applyDomReadingSettings = function (that) {
        that.setLayout(that);
        that.styleLinks(that);
        that.styleInputs(that);
        that.setIE6ColorInversion(that); 
    };

    /**
     * Transforms the interface based on the settings in that.model
     */
    fluid.uiEnhancer.refreshView = function (that) {
        that.textSize.set(that.model.textSize);
        that.textFont.swap(that.model.textFont);
        that.lineSpacing.set(that.model.lineSpacing);
        that.theme.swap(that.model.theme);
        $(document).ready(function () {
            fluid.uiEnhancer.applyTocSetting(that);
        });
    };


    /**
     * Adds or removes the classname to/from the elements based upon the setting.
     * @param {Object} elements
     * @param {Object} setting
     * @param {Object} classname
     */
    fluid.uiEnhancer.styleElements = function (elements, setting, classname) {
        if (setting) {
            elements.addClass(classname);
        } else {
            $("." + classname, elements).andSelf().removeClass(classname);
        }        
    };

    /**
     * Style layout in the container according to the settings
     * @param {Object} that - the uiEnhancer
     */
    fluid.uiEnhancer.setLayout = function (that) {
        that.styleElements(that.container, that.model.layout, that.options.classnameMap.layout);
    };

    /**
     * Style links in the container according to the settings
     * @param {Object} that - the uiEnhancer
     */
    fluid.uiEnhancer.styleLinks = function (that) {
        var links = $("a", that.container);
        that.styleElements(links, that.model.links, that.options.classnameMap.links);
    };

    /**
     * Style inputs in the container according to the settings
     * @param {Object} that - the uiEnhancer
     */
    fluid.uiEnhancer.styleInputs = function (that) {
        that.styleElements($("input, button", that.container), that.model.inputsLarger, that.options.classnameMap.inputsLarger);
    };

    /**
     * remove the instances of fl-inverted-color when the default theme is selected. 
     * This prevents a bug in IE6 where the default theme will have elements styled 
     * with the theme color.
     *
     * Caused by:
     * http://thunderguy.com/semicolon/2005/05/16/multiple-class-selectors-in-internet-explorer/
     * @param {Object} that - the uiEnhancer
     */
    fluid.uiEnhancer.setIE6ColorInversion = function (that) {
        if (fluid.hasFeature("fluid.browser.msie") && fluid.hasFeature("fluid.browser.majorVersion.6") && that.model.theme === "default") {
            that.locate("colorInversion").removeClass(that.options.styles.colorInversionClass);
        }
    };

    /**
     * return "font-size" in px
     * @param (Object) container
     * @param (Object) fontSizeMap: the mapping between the font size string values ("small", "medium" etc) to px values
     */
    fluid.uiEnhancer.getTextSizeInPx = function (container, fontSizeMap) {
        var fontSize = container.css("font-size");

        if (fontSizeMap[fontSize]) {
            fontSize = fontSizeMap[fontSize];
        }

        // return fontSize in px
        return parseFloat(fontSize);
    };

    /**
     * return "font-size" in em
     * @param (Object) container
     * @param (Object) fontSizeMap: the mapping between the font size string values ("small", "medium" etc) to px values
     */
    fluid.uiEnhancer.getTextSizeInEm = function (container, fontSizeMap) {
        var px2emFactor = fluid.uiEnhancer.getPx2EmFactor(container, fontSizeMap);

        // retrieve fontSize in px, convert and return in em 
        return Math.round(fluid.uiEnhancer.getTextSizeInPx(container, fontSizeMap) / px2emFactor * 10000) / 10000;
    };
    
    fluid.uiEnhancer.getPx2EmFactor = function (container, fontSizeMap) {
        // The base font size is the computed font size of the container's parent element unless the container itself has been a "body" tag
        if (container.get(0).tagName !== "BODY") {
            container = container.parent();
        }
        return fluid.uiEnhancer.getTextSizeInPx(container, fontSizeMap);
    };

    // Return "line-height" css value
    fluid.uiEnhancer.getLineHeight = function (container) {
        var lineHeight;
        
        // A work-around of jQuery + IE bug - http://bugs.jquery.com/ticket/2671
        if (container[0].currentStyle) {
            lineHeight = container[0].currentStyle.lineHeight;
        } else {
            lineHeight = container.css("line-height");
        }
        
        return lineHeight;
    };
    
    // Interprets browser returned "line-height" value, either a string "normal", a number with "px" suffix or "undefined" 
    // into a numeric value in em. 
    // Return 0 when the given "lineHeight" argument is "undefined" (http://issues.fluidproject.org/browse/FLUID-4500).
    fluid.uiEnhancer.numerizeLineHeight = function (lineHeight, fontSize) {
        // Handel the given "lineHeight" argument is "undefined", which occurs when firefox detects 
        // "line-height" css value on a hidden container. (http://issues.fluidproject.org/browse/FLUID-4500)
        if (!lineHeight) {
            return 0;
        }

        // Needs a better solution. For now, "line-height" value "normal" is defaulted to 1.2em
        // according to https://developer.mozilla.org/en/CSS/line-height
        if (lineHeight === "normal") {
            return 1.2;
        }
        
        // Continuing the work-around of jQuery + IE bug - http://bugs.jquery.com/ticket/2671
        if (lineHeight.match(/[0-9]$/)) {
            return lineHeight;
        }
        
        return Math.round(parseFloat(lineHeight) / fontSize * 100) / 100;
    };

    /*******************************************************************************
     * TextSizer                                                                   *
     *                                                                             *
     * Sets the text size on the container to the multiple provided.               *
     * Note: This will become half an ant                                          *
     *******************************************************************************/
    
    fluid.defaults("fluid.uiEnhancer.textSizer", {
        gradeNames: ["fluid.viewComponent", "autoInit"],
        invokers: {
            set: {
                funcName: "fluid.uiEnhancer.textSizer.set",
                args: ["@0", "{textSizer}"]
            }
        }
    });
       
    fluid.uiEnhancer.textSizer.set = function (times, that) {
        if (!that.initialSize) {
            that.initialSize = that.calcInitSize();
        }

        if (that.initialSize) {
            var targetSize = times * that.initialSize;
            that.container.css("font-size", targetSize + "em");
        }
    };
    
    fluid.uiEnhancer.textSizer.calcInitSize = function (container, fontSizeMap) {
        return fluid.uiEnhancer.getTextSizeInEm(container, fontSizeMap);
    };

    /*******************************************************************************
     * ClassSwapper                                                                *
     *                                                                             *
     * Has a hash of classes it cares about and will remove all those classes from *
     * its container before setting the new class.                                 *
     * Note: This will become half an ant                                          *
     *******************************************************************************/
    
    fluid.defaults("fluid.uiEnhancer.classSwapper", {
        gradeNames: ["fluid.viewComponent", "autoInit"],
        invokers: {
            clearClasses: {
                funcName: "fluid.uiEnhancer.classSwapper.clearClasses",
                args: ["{classSwapper}"]
            },
            swap: {
                funcName: "fluid.uiEnhancer.classSwapper.swap",
                args: ["@0", "{classSwapper}"]
            }
        },
        classes: {},
        finalInitFunction: "fluid.uiEnhancer.classSwapper.finalInit"
    });
    
    fluid.uiEnhancer.classSwapper.finalInit = function (that) {
        that.classSelector = "";
        that.classStr = "";
        
        fluid.each(that.options.classes, function (className) {
            if (className) {
                that.classSelector += that.classSelector ? ", ." + className : "." + className;
                that.classStr += that.classStr ? " " + className : className;
            }
        });
    };
    
    fluid.uiEnhancer.classSwapper.clearClasses = function (that) {
        that.container.removeClass(that.classStr);
    };
    
    fluid.uiEnhancer.classSwapper.swap = function (classname, that) {
        that.clearClasses(that);
        that.container.addClass(that.options.classes[classname]);
    };
    
    /*******************************************************************************
     * LineSpacer                                                                  *
     *                                                                             *
     * Sets the line spacing on the container to the multiple provided.            *
     * Note: This will become half an ant                                          *
     *******************************************************************************/
    
    fluid.defaults("fluid.uiEnhancer.lineSpacer", {
        gradeNames: ["fluid.viewComponent", "autoInit"],
        invokers: {
            set: {
                funcName: "fluid.uiEnhancer.lineSpacer.set",
                args: ["@0", "{lineSpacer}"]
            }
        }
    });
    
    // TODO: this might be almost the same as textSize setting - can we share?
    fluid.uiEnhancer.lineSpacer.set = function (times, that) {
        if (!that.initialSize) {
            that.initialSize = that.calcInitSize();
        }
        
        // that.initialSize === 0 when the browser returned "lineHeight" css value is undefined,
        // which occurs when firefox detects this value on a hidden container.
        // @ See fluid.uiEnhancer.numerizeLineHeight() & http://issues.fluidproject.org/browse/FLUID-4500
        if (that.initialSize) {
            var targetLineSpacing = times * that.initialSize;
            that.container.css("line-height", targetLineSpacing + "em");
        }
    };
    
    // Returns the value of css style "line-height" in em 
    fluid.uiEnhancer.lineSpacer.calcInitSize = function (container, fontSizeMap) {
        var lineHeight = fluid.uiEnhancer.getLineHeight(container);
        var fontSize = fluid.uiEnhancer.getTextSizeInPx(container, fontSizeMap);

        return fluid.uiEnhancer.numerizeLineHeight(lineHeight, fontSize);
    };
    
    /*******************************************************************************
     * PageEnhancer                                                                *
     *                                                                             *
     * A UIEnhancer wrapper that concerns itself with the entire page.             *
     *******************************************************************************/    
    
    fluid.pageEnhancer = function (uiEnhancerOptions) {
        var that = fluid.initLittleComponent("fluid.pageEnhancer");
        uiEnhancerOptions = fluid.copy(uiEnhancerOptions);
        // This hack is required to resolve FLUID-4409 - much improved framework support is required
        uiEnhancerOptions.originalUserOptions = fluid.copy(uiEnhancerOptions);
        that.uiEnhancerOptions = uiEnhancerOptions;
        fluid.initDependents(that);
        fluid.staticEnvironment.uiEnhancer = that.uiEnhancer;
        return that;
    };

    fluid.defaults("fluid.pageEnhancer", {
        gradeNames: ["fluid.littleComponent"],
        components: {
            uiEnhancer: {
                type: "fluid.uiEnhancer",
                container: "body",
                options: "{pageEnhancer}.uiEnhancerOptions"
            }
        }
    });
    
    fluid.demands("fluid.uiOptions.store", ["fluid.uiEnhancer"], {
        funcName: "fluid.cookieStore"
    });
    
})(jQuery, fluid_1_5);
/*
Copyright 2009 University of Toronto
Copyright 2010-2011 OCAD University
Copyright 2011 Lucendo Development Ltd.

Licensed under the Educational Community License (ECL), Version 2.0 or the New
BSD license. You may not use this file except in compliance with one these
Licenses.

You may obtain a copy of the ECL 2.0 License and BSD License at
https://github.com/fluid-project/infusion/raw/master/Infusion-LICENSE.txt
*/

// Declare dependencies
/*global fluid_1_5:true, jQuery*/

// JSLint options 
/*jslint white: true, funcinvoke: true, undef: true, newcap: true, nomen: true, regexp: true, bitwise: true, browser: true, forin: true, maxerr: 100, indent: 4 */

var fluid_1_5 = fluid_1_5 || {};


/******************
 * Textfield Slider *
 ******************/

(function ($, fluid) {

    fluid.defaults("fluid.textfieldSlider", {
        gradeNames: ["fluid.viewComponent", "autoInit"], 
        components: {
            textfield: {
                type: "fluid.textfieldSlider.textfield",
                container: "{textfieldSlider}.dom.textfield",
                options: {
                    model: "{textfieldSlider}.model",
                    applier: "{textfieldSlider}.applier"
                }
            },
            slider: {
                type: "fluid.textfieldSlider.slider",
                container: "{textfieldSlider}.dom.slider",
                options: {
                    model: "{textfieldSlider}.model",
                    applier: "{textfieldSlider}.applier",
                    sliderOptions: "{textfieldSlider}.options.sliderOptions"
                }
            }
        },
        selectors: {
            textfield: ".flc-textfieldSlider-field",
            slider: ".flc-textfieldSlider-slider"
        },
        events: {
            modelChanged: null
        },
        model: {
            value: null,
            min: 0,
            max: 100
        },
        sliderOptions: {
            orientation: "horizontal",
            step: 1.0
        }, 
        finalInitFunction: "fluid.textfieldSlider.finalInit"
    });    
    
    fluid.textfieldSlider.finalInit = function (that) {

        that.refreshView = function () {
            var val = that.model.value;
            that.textfield.container.val(val);
        };
        
        // TODO: replace this with "model events relay" system.
        // problem: if we place these directly in "events", this will destroy all
        // existing events named "modelChanged".
        that.applier.modelChanged.addListener("value", 
            function (newModel) {
                that.events.modelChanged.fire(newModel.value);
            }
        );

        that.events.modelChanged.addListener(that.refreshView);

        that.refreshView();
    };
    
    fluid.defaults("fluid.textfieldSlider.textfield", {
        gradeNames: ["fluid.viewComponent", "autoInit"],
        finalInitFunction: "fluid.textfieldSlider.textfield.finalInit"
    });

    fluid.textfieldSlider.validateValue = function (model, changeRequest, applier) {
        var oldValue = model.value;
        var newValue = changeRequest.value;
        
        var isValidNum = !isNaN(parseInt(newValue, 10));

        if (isValidNum) {
            if (newValue < model.min) {
                newValue = model.min;
            } else if (newValue > model.max) {
                newValue = model.max;
            }
            changeRequest.value = newValue;
        } else {
            changeRequest.value = oldValue;
        }
    };

    fluid.textfieldSlider.textfield.finalInit = function (that) {
        that.applier.guards.addListener({path: "value", transactional: true}, fluid.textfieldSlider.validateValue);
        
        that.container.change(function (source) {
            that.applier.requestChange("value", source.target.value);
        });
    };

    fluid.defaults("fluid.textfieldSlider.slider", {
        gradeNames: ["fluid.viewComponent", "autoInit"],
        finalInitFunction: "fluid.textfieldSlider.slider.finalInit",
        selectors: {
            thumb: ".ui-slider-handle"
        },
        events: {
            modelChanged: null
        },
    });
    
    // This will be removed once the jQuery UI slider has built in ARIA 
    var initSliderAria = function (thumb, opts) {
        var ariaDefaults = {
            role: "slider",
            "aria-valuenow": opts.value,
            "aria-valuemin": opts.min,
            "aria-valuemax": opts.max
        };
        thumb.attr(ariaDefaults);
    };
    
    fluid.textfieldSlider.slider.finalInit = function (that) {
        var sliderOptions = $.extend(true, {}, that.options.sliderOptions, that.model);
        
        that.slider = that.container.slider(sliderOptions);
        initSliderAria(that.locate("thumb"), sliderOptions);
        
        that.setSliderValue = function (value) {
            that.slider.slider("value", value);
        };
        
        that.setSliderAria = function (value) {
            that.locate("thumb").attr("aria-valuenow", value);
        };
        
        that.slider.bind("slide", function (e, ui) {
            that.applier.requestChange("value", ui.value);
        });
        
        that.applier.modelChanged.addListener("value", 
            function (newModel) {
                that.setSliderValue(newModel.value);
                that.setSliderAria(newModel.value);
                that.events.modelChanged.fire(newModel.value);
            }
        );
        
    };

})(jQuery, fluid_1_5);


/**************
 * UI Options *
 **************/

(function ($, fluid) {

    fluid.registerNamespace("fluid.uiOptions.inline");

    /*********************
     * UI Options Inline *
     *********************/

    /**
     * An UI Options top-level component that reflects the collaboration between uiOptionsLoader
     * and templateLoader. This component is the only UI Options component that is intended to be 
     * called by the outside world.
     * 
     * @param {Object} options
     */    
    fluid.defaults("fluid.uiOptions.inline", {
        gradeNames: ["fluid.viewComponent"],
        mergePolicy: {
            uiOptionsTransform: "noexpand",
            derivedDefaults: "noexpand"
        },
        components: {
            uiOptionsLoader: {
                type: "fluid.uiOptions.loader"
            },
            templateLoader: {
                priority: "first",
                type: "fluid.uiOptions.templateLoader"
            }
        },
        uiOptionsTransform: {
            transformer: "fluid.uiOptions.mapOptions",
            config: {
                "*.templateLoader":                                   "templateLoader",
                "*.templateLoader.*.templatePath.options.value":      "prefix",
                "*.uiOptionsLoader":                                  "uiOptionsLoader",
                "*.uiOptionsLoader.container":                        "container",
                "*.uiOptionsLoader.*.uiOptions":                      "uiOptions",
                "*.uiOptionsLoader.*.uiOptions.*.textControls":       "textControls",
                "*.uiOptionsLoader.*.uiOptions.*.layoutControls":     "layoutControls",
                "*.uiOptionsLoader.*.uiOptions.*.linksControls":      "linksControls",
                "*.uiOptionsLoader.*.uiOptions.*.mediaControls":      "mediaControls",
                "*.uiOptionsLoader.*.uiOptions.*.preview":            "preview",
                "*.uiOptionsLoader.*.uiOptions.*.preview.*.enhancer": "previewEnhancer"
            }
        },
        derivedDefaults: {
            uiOptions: {
                options: {
                    components: {
                        settingsStore: "{uiEnhancer}.settingsStore"
                    },
                    listeners: {
                        onUIOptionsRefresh: "{uiEnhancer}.updateFromSettingsStore"
                    }
                }
            }
        }
    });
    
    fluid.uiOptions.inline.makeCreator = function (componentName, processor) {
        fluid.setGlobalValue(componentName, function (container, options) {
            // make "container" one of the options so it can be munged by the uiOptions.mapOptions.
            // This container is passed down to be used as uiOptionsLoader.container
            var defaults = fluid.defaults(componentName);
            options.container = container;
            options = processor(options);
            
            var mappedOptions = fluid.uiOptions.mapOptions(options, defaults.uiOptionsTransform.config, defaults.mergePolicy, 
                fluid.copy(defaults.derivedDefaults));
            var that = fluid.initView(componentName, container, mappedOptions);
            // Fake out standard framework failed view diagnosis to prevent "that is null" message - remove this in 1.5
            fluid.diagnoseFailedView(componentName, that, fluid.defaults(componentName), [componentName, container, mappedOptions]);
            fluid.initDependents(that);
            return that;
        });
    };
    
    /**
    * @param {Object} inObject, the element on inObject is in the pair of key -> value
    */
    fluid.uiOptions.sortByKeyLength = function (inObject) {
        var keys = fluid.keys(inObject);
        return keys.sort(fluid.compareStringLength(true));
    };
    
    fluid.uiOptions.mapOptionsRecord = function (options, sortedConfigKeys, config) {
        var opRecs = [{}, {}, options || {}];
        var appliers = fluid.transform(opRecs, function (opRec) {
            return fluid.makeChangeApplier(opRec);
        });
        var toDelete = [];
        fluid.each(sortedConfigKeys, function (origDest) {
            var source = config[origDest];
            var dest = fluid.uiOptions.expandShortPath(origDest);
            var applier = appliers[origDest.charAt(0) === "!" ? 0 : 1];
            
            // Process the user pass-in options
            var value = fluid.get(options, source);
            if (value) {
                applier.requestChange(dest, value, "ADD");
                toDelete.push({source: source, value: value});
            }
        });
        fluid.each(toDelete, function(elem) {
            appliers[2].requestChange(elem.source, elem.value, "DELETE");
        });
        return opRecs;
    };
    
    // TODO: This dreadful function will be absorbed into the framework for 1.5
    /**
    * @param {Object} options, top level options to be mapped
    * @param {Array} config, a mapping between the target path on the IoC tree and the option name
    * @param {Object} used in fluid.merge() to merge options and componentConfig
    */
    fluid.uiOptions.mapOptions = function (options, config, mergePolicy, derivedDefaults) {
        // Sort the config object by the length of the key in case an option and its child option
        // are both configurable. 
        // For instance: "*.templateLoader" & "*.templateLoader.*.templatePath.options.value"
        var sortedConfigKeys = fluid.uiOptions.sortByKeyLength(config);         

        var optrecs = fluid.uiOptions.mapOptionsRecord(options, sortedConfigKeys, config);
        var devrecs = fluid.uiOptions.mapOptionsRecord(derivedDefaults, sortedConfigKeys, config);
        var mergeOpts = [mergePolicy].concat(devrecs).concat(optrecs);
        return fluid.merge.apply(null, mergeOpts);
    };
    
    fluid.uiOptions.expandShortPath = function (path) {
        if (path.charAt(0) === "!") {
            path = path.substring(1);
        }
        var strToreplaceFirst = "components";
        var strToreplaceRest = "options.components";

        // replace the beginning "*"
        var newPath = (path.charAt(0) === "*") ? path.replace("*", strToreplaceFirst) : path;

        // replace the rest "*"
        newPath = newPath.replace(/\*/g, strToreplaceRest);
        
        return newPath;
    };
    
    /******************************
     * UI Options Template Loader *
     ******************************/

    /**
     * A configurable component that works in conjunction with or without the UI Options template path  
     * component (fluid.uiOptionsTemplatePath) to allow users to set either the location of their own 
     * templates or the templates that are relative to the path defined in the UI Options template path 
     * component.
     * 
     * @param {Object} options
     */    
       
    fluid.defaults("fluid.uiOptions.templateLoader", {
        gradeNames: ["fluid.eventedComponent", "autoInit"],
        finalInitFunction: "fluid.uiOptions.templateLoader.resolveTemplates",
        templates: {
            uiOptions: "%prefix/FatPanelUIOptions.html",
            textControls: "%prefix/UIOptionsTemplate-text.html",
            layoutControls: "%prefix/UIOptionsTemplate-layout.html",
            linksControls: "%prefix/UIOptionsTemplate-links.html",
            mediaControls: "%prefix/UIOptionsTemplate-media.html"
        },
        // Unsupported, non-API option
        components: {
            templatePath: {
                type: "fluid.uiOptions.templatePath"
            }
        },
        invokers: {
            transformURL: {
                funcName: "fluid.stringTemplate",
                args: [ "{arguments}.0", { "prefix/" : "{templateLoader}.templatePath.options.value"} ]
            }
        }
    });

    fluid.uiOptions.templateLoader.resolveTemplates = function (that) {
        var mapped = fluid.transform(that.options.templates, that.transformURL);
    
        that.resources = fluid.transform(mapped, function (url) {
            return {url: url, forceCache: true};
        });
    };
    
    /**************************************
     * UI Options Template Path Specifier *
     **************************************/
    
    /**
     * A configurable component that defines the relative path from the html to UI Options templates.
     * 
     * @param {Object} options
     */
    
    fluid.defaults("fluid.uiOptions.templatePath", {
        gradeNames: ["fluid.littleComponent", "autoInit"],
        value: "../html/"
    });
    
    /**************
     * UI Options *
     **************/
    
    fluid.defaults("fluid.uiOptions.loader", {
        gradeNames: ["fluid.viewComponent", "autoInit"],
        resources: "{templateLoader}.resources",
        finalInitFunction: "fluid.uiOptions.loader.finalInit",
        events: {
            // These two are events private to uiOptions
            onUIOptionsTemplateReady: null, // templates are loaded - construct UIOptions itself
            onUIOptionsComponentReady: null, // UIOptions is loaded - construct its subcomponents
            // This is a public event which users outside the component can subscribe to - the argument
            // supplied is UIOptions.loader itself
            onReady: null
        },
        listeners: {
            onUIOptionsComponentReady: {
                listener: "{loader}.events.onReady",
                args: ["{fluid.uiOptions.loader}", "{arguments}.0"],
                priority: "last"
            }
        },
        components: {
            uiOptions: {
                type: "fluid.uiOptions",
                container: "{loader}.container",
                createOnEvent: "onUIOptionsTemplateReady",
                options: {
                    events: {
                        "onUIOptionsComponentReady": "{loader}.events.onUIOptionsComponentReady"
                    }
                }
            }
        }
    });
    
    fluid.uiOptions.loader.finalInit = function (that) {
        fluid.fetchResources(that.options.resources, function () {that.events.onUIOptionsTemplateReady.fire();});
    };

    /**
     * A component that works in conjunction with the UI Enhancer component and the Fluid Skinning System (FSS) 
     * to allow users to set personal user interface preferences. The UI Options component provides a user 
     * interface for setting and saving personal preferences, and the UI Enhancer component carries out the 
     * work of applying those preferences to the user interface.
     * 
     * @param {Object} container
     * @param {Object} options
     */
    fluid.defaults("fluid.uiOptions", {
        gradeNames: ["fluid.viewComponent", "autoInit"],
        components: {
            textControls: {
                type: "fluid.uiOptions.textControls",
                container: "{uiOptions}.dom.textControls",
                createOnEvent: "onUIOptionsComponentReady",
                options: {
                    model: "{uiOptions}.model",
                    applier: "{uiOptions}.applier",
                    classnameMap: "{uiEnhancer}.options.classnameMap",
                    rendererOptions: "{uiOptions}.options.rendererOptions",
                    events: {
                        onUIOptionsRefresh: "{uiOptions}.events.onUIOptionsRefresh"
                    }
                }
            },
            layoutControls: {
                type: "fluid.uiOptions.layoutControls",
                container: "{uiOptions}.dom.layoutControls",
                createOnEvent: "onUIOptionsComponentReady",
                options: {
                    model: "{uiOptions}.model",
                    applier: "{uiOptions}.applier",
                    classnameMap: "{uiEnhancer}.options.classnameMap",
                    rendererOptions: "{uiOptions}.options.rendererOptions",
                    events: {
                        onUIOptionsRefresh: "{uiOptions}.events.onUIOptionsRefresh"
                    }
                }
            },
            linksControls: {
                type: "fluid.uiOptions.linksControls",
                container: "{uiOptions}.dom.linksControls",
                createOnEvent: "onUIOptionsComponentReady",
                options: {
                    model: "{uiOptions}.model",
                    applier: "{uiOptions}.applier",
                    classnameMap: "{uiEnhancer}.options.classnameMap",
                    rendererOptions: "{uiOptions}.options.rendererOptions",
                    events: {
                        onUIOptionsRefresh: "{uiOptions}.events.onUIOptionsRefresh"
                    }
                }
            },
            mediaControls: {
                type: "fluid.uiOptions.mediaControls",
                container: "{uiOptions}.dom.mediaControls",
                createOnEvent: "onUIOptionsComponentReady",
                options: {
                    model: "{uiOptions}.model",
                    applier: "{uiOptions}.applier",
                    rendererOptions: "{uiOptions}.options.rendererOptions",
                    events: {
                        onUIOptionsRefresh: "{uiOptions}.events.onUIOptionsRefresh"
                    }
                }
            },
            preview: {
                type: "fluid.uiOptions.preview",
                createOnEvent: "onUIOptionsComponentReady",
                container: "{uiOptions}.dom.previewFrame"
            },
            eventBinder: {
                type: "fluid.uiOptions.eventBinder"
            }
        },
        selectors: {
            textControls: ".flc-uiOptions-text-controls",
            layoutControls: ".flc-uiOptions-layout-controls",
            linksControls: ".flc-uiOptions-links-controls",
            mediaControls: ".flc-uiOptions-media-controls",
            cancel: ".flc-uiOptions-cancel",
            reset: ".flc-uiOptions-reset",
            save: ".flc-uiOptions-save",
            previewFrame : ".flc-uiOptions-preview-frame"
        },
        events: {
            onSave: null,
            onCancel: null,
            onReset: null,
            onAutoSave: null,
            modelChanged: null,
            onUIOptionsRefresh: null,
            onUIOptionsComponentReady: null
        },
        finalInitFunction: "fluid.uiOptions.finalInit",
        resources: {
            template: "{templateLoader}.resources.uiOptions"
        },
        autoSave: false
    });

    fluid.uiOptions.finalInit = function (that) {
        that.applier.requestChange("selections", fluid.copy(that.settingsStore.fetch()));

        /**
         * Saves the current model and fires onSave
         */ 
        that.save = function () {
            that.events.onSave.fire(that.model.selections);
            
            var savedSelections = fluid.copy(that.model.selections);
            that.settingsStore.save(savedSelections);
        };
        
        that.saveAndApply = function () {
            that.save();
            that.events.onUIOptionsRefresh.fire();
        };


        /**
         * Resets the selections to the integrator's defaults and fires onReset
         */
        that.reset = function () {
            that.updateModel(fluid.copy(that.settingsStore.options.defaultSiteSettings));
            that.events.onReset.fire(that);
            that.events.onUIOptionsRefresh.fire();
        };
        
        /**
         * Resets the selections to the last saved selections and fires onCancel
         */
        that.cancel = function () {
            that.events.onCancel.fire();
            that.updateModel(that.settingsStore.fetch());
            that.events.onUIOptionsRefresh.fire();
        };
        
        /**
         * Updates the change applier and fires modelChanged on subcomponent fluid.uiOptions.controls
         * 
         * @param {Object} newModel
         * @param {Object} source
         */
        that.updateModel = function (newModel) {
            that.applier.requestChange("selections", newModel);
        };
        
        that.applier.modelChanged.addListener("selections",
            function (newModel, oldModel, changeRequest) {
                that.events.modelChanged.fire(newModel, oldModel, changeRequest.source);
                if (that.options.autoSave) {
                    that.events.onAutoSave.fire();
                }
            }
            );
            
        var bindHandlers = function (that) {
            var saveButton = that.locate("save");            
            if (saveButton.length > 0) {
                saveButton.click(that.saveAndApply);
                var form = fluid.findForm(saveButton);
                $(form).submit(function () {
                    that.saveAndApply();
                });
            }
            that.locate("reset").click(that.reset);
            that.locate("cancel").click(that.cancel);
        };
        
        var bindEventHandlers = function (that) {
            that.events.onAutoSave.addListener(function () {
                that.save();    
            });
        };
        
        fluid.fetchResources(that.options.resources, function () {
          // This setTimeout is to ensure that fetching of resources is asynchronous,
          // and so that component construction does not run ahead of subcomponents for FatPanel
          // (FLUID-4453 - this may be a replacement for a branch removed for a FLUID-2248 fix) 
            setTimeout(function () {
                that.container.append(that.options.resources.template.resourceText);
                bindHandlers(that);
                bindEventHandlers(that);
                that.events.onUIOptionsComponentReady.fire(that);
            }, 1);
        });
    };

    /******************************************************
     * UI Options Event binder:                           *
     * Binds events between UI Options and the UIEnhancer *
     ******************************************************/
     
    fluid.defaults("fluid.uiOptions.eventBinder", {
        gradeNames: ["fluid.eventedComponent", "autoInit"]
    });

    var optionsToLabelMap = function (that) {
        fluid.each(that.options.controlValues, function (item, key) {
            that.applier.requestChange("labelMap." + key, {
                values: that.options.controlValues[key],
                names: that.options.strings[key],
                classes: fluid.get(that, "options.classnameMap."+key)
            });
        });
    };
    
    var createSliderNode = function (that, item, type, options) {
        return {
            decorators: {
                type: "fluid",
                func: type,
                options: {
                    listeners: {
                        modelChanged: function (value) {
                            that.applier.requestChange("selections." + item, value);
                        }
                    },
                    model: {
                        min: that.options[item].min,
                        max: that.options[item].max,
                        value: that.model.selections[item]
                        
                    },
                    sliderOptions: that.options[item].sliderOptions
                }
            }
        };
    };
    
    fluid.uiOptions.controlsFinalInit = function (that) {
        optionsToLabelMap(that);
        that.refreshView();        
    };
    
    // This function compensates for a framework deficiency that due to lack of gingerness, the "refreshView"
    // function synthesized by rendererComponent is not available during listener registration which only 
    // occurs after component init functions have completed (http://issues.fluidproject.org/browse/FLUID-4334)
    fluid.uiOptions.lateRefreshViewBinder = function (that) {
        that.refreshView = function () {
            that.renderer.refreshView();
        };
    };

    /****************************
     * UI Options Text Controls *
     ****************************/

    /**
     * A sub-component of fluid.uiOptions that renders the "text and display" panel of the user preferences interface.
     */
    fluid.defaults("fluid.uiOptions.textControls", {
        gradeNames: ["fluid.rendererComponent", "autoInit"], 
        strings: {
            textFont: ["Default", "Times New Roman", "Comic Sans", "Arial", "Verdana"],
            theme: ["Default", "Black on white", "White on black", "Black on yellow", "Yellow on black"]
        },
        controlValues: { 
            textFont: ["default", "times", "comic", "arial", "verdana"],
            theme: ["default", "bw", "wb", "by", "yb"]
        },
        textSize: {
            min: 1,
            max: 2,
            sliderOptions: {
                orientation: "horizontal",
                step: 0.1
            } 
        },
        lineSpacing: {
            min: 1,
            max: 2,
            sliderOptions: {
                orientation: "horizontal",
                step: 0.1
            } 
        },
        selectors: {
            textFont: ".flc-uiOptions-text-font",
            theme: ".flc-uiOptions-theme",
            textSize: ".flc-uiOptions-min-text-size",
            lineSpacing: ".flc-uiOptions-line-spacing"
        },
        events: {
            onUIOptionsRefresh: null    
        },
        listeners: {
            onUIOptionsRefresh: "{textControls}.refreshView"     
        },
        preInitFunction: "fluid.uiOptions.lateRefreshViewBinder",
        finalInitFunction: "fluid.uiOptions.controlsFinalInit",
        produceTree: "fluid.uiOptions.textControls.produceTree",
        resources: {
            template: "{templateLoader}.resources.textControls"
        }
    });
    
    fluid.uiOptions.textControls.produceTree = function (that) {
        var tree = {};
        
        for (var item in that.model.selections) {
            if (item === "textFont" || item === "theme") {
                // render drop down list box
                tree[item] = {
                    optionnames: "${labelMap." + item + ".names}",
                    optionlist: "${labelMap." + item + ".values}",
                    selection: "${selections." + item + "}",
                    decorators: {
                        type: "fluid",
                        func: "fluid.uiOptions.selectDecorator",
                        options: {
                            styles: that.options.classnameMap[item]
                        }
                    }
                };
            } else if (item === "textSize" || item === "lineSpacing") {
                // textfield sliders
                tree[item] = createSliderNode(that, item, "fluid.textfieldSlider");
            }
        }
        
        return tree;
    };

    /***********************************************
     * UI Options Select Dropdown Options Decorator*
     ***********************************************/

    /**
     * A sub-component that decorates the options on the select dropdown list box with the css style
     */
    fluid.demands("fluid.uiOptions.selectDecorator", "fluid.uiOptions", {
        container: "{arguments}.0"
    });
    
    fluid.defaults("fluid.uiOptions.selectDecorator", {
        gradeNames: ["fluid.viewComponent", "autoInit"], 
        finalInitFunction: "fluid.uiOptions.selectDecorator.finalInit",
        styles: {
            preview: "fl-preview-theme"
        }
    });
    
    fluid.uiOptions.selectDecorator.finalInit = function (that) {
        fluid.each($("option", that.container), function (option) {
            var styles = that.options.styles;
            $(option).addClass(styles.preview + " " + styles[fluid.value(option)]);
        });
    };
    
    /******************************
     * UI Options Layout Controls *
     ******************************/

    /**
     * A sub-component of fluid.uiOptions that renders the "layout and navigation" panel of the user preferences interface.
     */
    fluid.defaults("fluid.uiOptions.layoutControls", {
        gradeNames: ["fluid.rendererComponent", "autoInit"], 
        selectors: {
            layout: ".flc-uiOptions-layout",
            toc: ".flc-uiOptions-toc"
        },
        events: {
            onUIOptionsRefresh: null    
        },
        listeners: {
            onUIOptionsRefresh: "{layoutControls}.refreshView"     
        },
        preInitFunction: "fluid.uiOptions.lateRefreshViewBinder",
        finalInitFunction: "fluid.uiOptions.controlsFinalInit",
        produceTree: "fluid.uiOptions.layoutControls.produceTree",
        resources: {                    
            template: "{templateLoader}.resources.layoutControls"
        }
    });

    fluid.uiOptions.layoutControls.produceTree = function (that) {
        var tree = {};
        
        for (var item in that.model.selections) {
            if (item === "layout" || item === "toc") {
                // render radio buttons
                tree[item] = "${selections." + item + "}";
            }
        }
        
        return tree;
    };

    /*****************************
     * UI Options Links Controls *
     *****************************/
    /**
     * A sub-component of fluid.uiOptions that renders the "links and buttons" panel of the user preferences interface.
     */
    fluid.defaults("fluid.uiOptions.linksControls", {
        gradeNames: ["fluid.rendererComponent", "autoInit"], 
        selectors: {
            links: ".flc-uiOptions-links",
            inputsLarger: ".flc-uiOptions-inputs-larger"
        },
        events: {
            onUIOptionsRefresh: null    
        },
        listeners: {
            onUIOptionsRefresh: "{linksControls}.refreshView"     
        },
        preInitFunction: "fluid.uiOptions.lateRefreshViewBinder",
        finalInitFunction: "fluid.uiOptions.controlsFinalInit",
        produceTree: "fluid.uiOptions.linksControls.produceTree",
        resources: {
            template: "{templateLoader}.resources.linksControls"
        }
    });

    fluid.uiOptions.linksControls.produceTree = function (that) {
        var tree = {};
        
        for (var item in that.model.selections) {
            if (item === "links" || item === "inputsLarger") {
                // render check boxes
                tree[item] = "${selections." + item + "}";
            }
        }

        return tree;
    };

    /*****************************
     * UI Options Media Controls *
     *****************************/
    /**
     * A sub-component of fluid.uiOptions that renders the "media" panel of the user preferences interface.
     */
    fluid.defaults("fluid.uiOptions.mediaControls", {
        gradeNames: ["fluid.rendererComponent", "autoInit"], 
        strings: {
            language: ["English", "French"]
        },
        controlValues: {
            language: ["en", "fr"] 
        },
        volume: {
            min: 0,
            max: 100,
            sliderOptions: {
                orientation: "horizontal",
                step: 10
            }
        },
        selectors: {
            volume: ".flc-uiOptions-volume",
            captions: ".flc-uiOptions-captions",
            transcripts: ".flc-uiOptions-transcripts",
            language: ".flc-uiOptions-language"
        },
        events: {
            onUIOptionsRefresh: null    
        },
        listeners: {
            onUIOptionsRefresh: "{mediaControls}.refreshView"     
        },

        preInitFunction: "fluid.uiOptions.lateRefreshViewBinder",
        finalInitFunction: "fluid.uiOptions.controlsFinalInit",
        produceTree: "fluid.uiOptions.mediaControls.produceTree",
        resources: {
            template: "{templateLoader}.resources.mediaControls"
        }
    });

    fluid.uiOptions.mediaControls.produceTree = function (that) {
        var tree = {};
        for (var item in that.model.selections) {
            if (item === "captions" || item === "transcripts") {
                // render check boxes
                tree[item] = "${selections." + item + "}";
            } else if (item === "language") {
                tree[item] = {
                    optionnames: "${labelMap." + item + ".names}",
                    optionlist: "${labelMap." + item + ".values}",
                    selection: "${selections.language}",
                }
            } else if (item === "volume") {
                tree[item] = createSliderNode(that, item, "fluid.textfieldSlider.slider");
            }
        }

        return tree;
    };


    /**********************
     * UI Options Preview *
     **********************/

    fluid.defaults("fluid.uiOptions.preview", {
        gradeNames: ["fluid.viewComponent", "autoInit"], 
        components: {
            enhancer: {
                type: "fluid.uiEnhancer",
                createOnEvent: "onReady",
                options: {
                    settingsStore: {
                        type: "fluid.uiEnhancer.tempStore"
                    }
                }
            },
            eventBinder: {
                type: "fluid.uiOptions.preview.eventBinder",
                createOnEvent: "onReady"
            },
            // TODO: This is a violation of containment, but we can't use up our allowance of demands
            // blocks as a result of FLUID-4392
            templateLoader: "{templateLoader}"
        },
        invokers: {
            updateModel: {
                funcName: "fluid.uiOptions.preview.updateModel",
                args: [
                    "{preview}",
                    "{uiOptions}.model.selections"
                ]
            }
        },
        finalInitFunction: "fluid.uiOptions.preview.finalInit",
        events: {
            onReady: null
        },
        
        templateUrl: "%prefix/UIOptionsPreview.html"
    });
    
    fluid.uiOptions.preview.updateModel = function (that, selections) {
        /**
         * Setimeout is temp fix for http://issues.fluidproject.org/browse/FLUID-2248
         */
        setTimeout(function () {
            if (that.enhancer) {
                that.enhancer.updateModel(selections);
            }
        }, 0);
    };
    
    fluid.uiOptions.preview.finalInit = function (that) {
        var templateUrl = that.templateLoader.transformURL(that.options.templateUrl);
        that.container.load(function () {
            that.enhancerContainer = $("body", that.container.contents());
            that.events.onReady.fire();
        });
        that.container.attr("src", templateUrl);        

    };

    fluid.demands("fluid.uiEnhancer", "fluid.uiOptions.preview", {
        funcName: "fluid.uiEnhancer",
        args: [
            "{preview}.enhancerContainer",
            "{options}"
        ]
    });
    
    /***************************************************
     * UI Options Event binder:                        *
     * Binds events between UI Options and the Preview *
     ***************************************************/
     
    fluid.defaults("fluid.uiOptions.preview.eventBinder", {
        gradeNames: ["fluid.eventedComponent", "autoInit"]
    });
    
    fluid.demands("fluid.uiOptions.preview.eventBinder", ["fluid.uiOptions.preview", "fluid.uiOptions"], {
        options: {
            listeners: {
                "{uiOptions}.events.modelChanged": "{preview}.updateModel"
            }
        }
    });

})(jQuery, fluid_1_5);
/*
Copyright 2011 OCAD University
Copyright 2011 Lucendo Development Ltd.

Licensed under the Educational Community License (ECL), Version 2.0 or the New
BSD license. You may not use this file except in compliance with one these
Licenses.

You may obtain a copy of the ECL 2.0 License and BSD License at
https://github.com/fluid-project/infusion/raw/master/Infusion-LICENSE.txt
*/

// Declare dependencies
/*global fluid_1_5:true, jQuery, window*/

// JSLint options 
/*jslint white: true, funcinvoke: true, undef: true, newcap: true, nomen: true, regexp: true, bitwise: true, browser: true, forin: true, maxerr: 100, indent: 4 */

var fluid_1_5 = fluid_1_5 || {};

(function ($, fluid) {

    fluid.registerNamespace("fluid.dom");
    
    fluid.dom.getDocumentHeight = function (dokkument) {
        var body = $("body", dokkument)[0]; 
        return body.offsetHeight;
    };

    /*****************************************
     * Fat Panel UI Options Top Level Driver *
     *****************************************/ 


    fluid.defaults("fluid.uiOptions.fatPanel", {
        gradeNames: ["fluid.uiOptions.inline"],
        events: {
            afterRender: null,
            onReady: null
        },
        listeners: {
            onReady: {
                listener: "fluid.uiOptions.fatPanel.bindEvents",
                args: ["{arguments}.0.uiOptions", "{uiEnhancer}", "{iframeRenderer}.iframeEnhancer", "{fatPanel}"]
            }
        },
        selectors: {
            iframe: ".flc-uiOptions-iframe"
        },
        components: {
            pageEnhancer: "{uiEnhancer}",
            slidingPanel: {
                type: "fluid.slidingPanel",
                container: "{fatPanel}.container",
                options: {
                    invokers: {
                        operateShow: {
                            funcName: "fluid.uiOptions.fatPanel.showPanel"
                        },
                        operateHide: {
                            funcName: "fluid.uiOptions.fatPanel.hidePanel"
                        } 
                    }
                },
                createOnEvent: "afterRender"
            },
            iframeRenderer: {
                type: "fluid.uiOptions.fatPanel.renderIframe",
                container: "{fatPanel}.dom.iframe",
                options: {
                    markupProps: {
                        src: "%prefix/FatPanelUIOptionsFrame.html"
                    },
                    events: {
                        afterRender: "{fatPanel}.events.afterRender"
                    },
                    components: {
                        iframeEnhancer: {
                            type: "fluid.uiEnhancer",
                            container: "{iframeRenderer}.renderUIOContainer",
                            createOnEvent: "afterRender",
                            options: {
                                components: {
                                    settingsStore: "{pageEnhancer}.settingsStore"  
                                },
                                jQuery: "{iframeRenderer}.jQuery",
                                tocTemplate: "{pageEnhancer}.options.tocTemplate"
                            }
                        }
                    }
                }
            }
        },
        // TODO: This material is not really transformation, but would be better expressed by
        // FLUID-4392 additive demands blocks
        derivedDefaults: {
            uiOptionsLoader: {
                options: {
                    events: {
                        templatesAndIframeReady: {
                            events: {
                                iframeReady: "{fatPanel}.events.afterRender",
                                templateReady: "onUIOptionsTemplateReady"
                            }  
                        },
                        onReady: "{fatPanel}.events.onReady"
                    }
                }
            },
            uiOptions: {
                createOnEvent: "templatesAndIframeReady",
                container: "{iframeRenderer}.renderUIOContainer",
                options: {
                    // ensure that model and applier are available to users at top level
                    model: "{fatPanel}.model",
                    applier: "{fatPanel}.applier",
                    events: {
                        onSignificantDOMChange: null  
                    },
                    components: {
                        iframeRenderer: "{fatPanel}.iframeRenderer",
                        settingsStore: "{uiEnhancer}.settingsStore",
                        preview: {
                            type: "fluid.emptySubcomponent"
                        },
                        tabs: {
                            type: "fluid.tabs",
                            container: "{uiOptions}.container",
                            createOnEvent: "onUIOptionsComponentReady",
                            options: {
                                listeners: {
                                    tabsshow: {
                                        listener: "{uiOptions}.events.onSignificantDOMChange"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        uiOptionsTransform: {
            config: { // For FLUID-4409
                "!*.iframeRenderer.*.iframeEnhancer.options":  "outerEnhancerOptions",
                "*.slidingPanel":                              "slidingPanel",
                "*.iframeRenderer":                            "iframeRenderer",
                "*.iframeRenderer.options.prefix":             "prefix",
                "selectors.iframe":                            "iframe"
            }
        }
    });
    
        
    fluid.uiOptions.inline.makeCreator("fluid.uiOptions.fatPanel", function (options) {
        var enhancerOptions = fluid.get(fluid, "staticEnvironment.uiEnhancer.options.originalUserOptions");
        options.outerEnhancerOptions = enhancerOptions;
        return options;
    });
    
    /*****************************************
     * fluid.uiOptions.fatPanel.renderIframe *
     *****************************************/
    
    fluid.defaults("fluid.uiOptions.fatPanel.renderIframe", {
        gradeNames: ["fluid.viewComponent", "autoInit"],
        finalInitFunction: "fluid.uiOptions.fatPanel.renderIframe.finalInit",
        events: {
            afterRender: null
        },
        styles: {
            containerFlex: "fl-container-flex",
            container: "fl-uiOptions-fatPanel-iframe"
        },
        prefix: "./",
        markupProps: {
            // This overflow specification fixes anomalous x overflow on FF, but may not on IE
            style: "overflow-x:hidden; overflow-y:auto;",
            "class": "flc-iframe",
            src: "%prefix/uiOptionsIframe.html"
        }
    });
    
    fluid.uiOptions.fatPanel.renderIframe.finalInit = function (that) {
        var styles = that.options.styles;
        // TODO: get earlier access to templateLoader, 
        that.options.markupProps.src = fluid.stringTemplate(that.options.markupProps.src, {"prefix/": that.options.prefix});
        that.iframeSrc = that.options.markupProps.src;
        
        //create iframe and append to container
        that.iframe = $("<iframe/>");
        that.iframe.load(function () {
            var iframeWindow = that.iframe[0].contentWindow;
            that.iframeDocument = iframeWindow.document;

            //var iframeDoc = that.iframe.contents();
            that.jQuery = iframeWindow.jQuery;
            that.renderUIOContainer = that.jQuery("body", that.iframeDocument);
            that.jQuery(that.iframeDocument).ready(that.events.afterRender.fire);
        });
        that.iframe.attr(that.options.markupProps);
        
        that.iframe.addClass(styles.containerFlex);
        that.iframe.addClass(styles.container);

        that.iframe.appendTo(that.container);
    };
        
    fluid.uiOptions.fatPanel.updateView = function (uiOptions, uiEnhancer) {
        uiEnhancer.updateFromSettingsStore();
        uiOptions.events.onSignificantDOMChange.fire();
    };
    
    fluid.uiOptions.fatPanel.bindEvents = function (uiOptions, uiEnhancer, iframeEnhancer, fatPanel) {
        // TODO: This binding should be done declaratively - needs ginger world in order to bind onto slidingPanel
        // which is a child of this component - and also uiOptionsLoader which is another child
        fatPanel.slidingPanel.events.afterPanelShow.addListener(function () {
            fluid.uiOptions.fatPanel.updateView(uiOptions, iframeEnhancer);
        });  
    
        uiOptions.events.modelChanged.addListener(function (model) {
            uiEnhancer.updateModel(model.selections);
            uiOptions.save();
        });
        uiOptions.events.onReset.addListener(function (uiOptions) {
            fluid.uiOptions.fatPanel.updateView(uiOptions, iframeEnhancer);
        });
        uiOptions.events.onSignificantDOMChange.addListener(function () {
            var dokkument = uiOptions.container[0].ownerDocument;
            var height = fluid.dom.getDocumentHeight(dokkument);
            var iframe = fatPanel.iframeRenderer.iframe;
            var attrs = {height: height + 15}; // TODO: Configurable padding here
            var panel = fatPanel.slidingPanel.locate("panel");
            panel.css({height: ""});
            iframe.animate(attrs, 400);
        });
        
        fatPanel.slidingPanel.events.afterPanelHide.addListener(function () {
            fatPanel.iframeRenderer.iframe.height(0);
        });
    };

    // Replace the standard animator since we don't want the panel to become hidden
    // (potential cause of jumping)
    fluid.uiOptions.fatPanel.hidePanel = function (panel, callback) {
        $(panel).animate({height: 0}, {duration: 400, complete: callback});
    };
    
    // no activity - the kickback to the updateView listener will automatically trigger the
    // DOMChangeListener above. This ordering is preferable to avoid causing the animation to
    // jump by refreshing the view inside the iframe
    fluid.uiOptions.fatPanel.showPanel = function (panel, callback) {
        // A bizarre race condition has emerged under FF where the iframe held within the panel does not
        // react synchronously to being shown
        setTimeout(callback, 1);
    };
    
})(jQuery, fluid_1_5);/*
Copyright 2011 OCAD University
Copyright 2011 Lucendo Development Ltd.

Licensed under the Educational Community License (ECL), Version 2.0 or the New
BSD license. You may not use this file except in compliance with one these
Licenses.

You may obtain a copy of the ECL 2.0 License and BSD License at
https://github.com/fluid-project/infusion/raw/master/Infusion-LICENSE.txt
*/

// Declare dependencies
/*global fluid_1_5:true, jQuery*/

// JSLint options 
/*jslint white: true, funcinvoke: true, undef: true, newcap: true, nomen: true, regexp: true, bitwise: true, browser: true, forin: true, maxerr: 100, indent: 4 */

var fluid_1_5 = fluid_1_5 || {};

(function ($, fluid) {
    /******************************
     * Full No Preview UI Options *
     ******************************/

    fluid.defaults("fluid.uiOptions.fullNoPreview", {
        gradeNames: ["fluid.uiOptions.inline"],
        container: "{fullNoPreview}.container",
        derivedDefaults: {
            templateLoader: {
                options: {
                    templates: {
                        uiOptions: "%prefix/FullNoPreviewUIOptions.html"
                    }
                }
            },
            uiOptions: {
                options: {
                    components: {
                        preview: {
                            type: "fluid.emptySubcomponent"
                        }
                    },
                    listeners: {
                        onReset: function (uiOptions) {
                            uiOptions.save();
                        }
                    }
                }
            }
        }
    });
    
    fluid.uiOptions.inline.makeCreator("fluid.uiOptions.fullNoPreview", fluid.identity); 
    
})(jQuery, fluid_1_5);/*
Copyright 2011 OCAD University
Copyright 2011 Lucendo Development Ltd.

Licensed under the Educational Community License (ECL), Version 2.0 or the New
BSD license. You may not use this file except in compliance with one these
Licenses.

You may obtain a copy of the ECL 2.0 License and BSD License at
https://github.com/fluid-project/infusion/raw/master/Infusion-LICENSE.txt
*/

// Declare dependencies
/*global fluid_1_5:true, jQuery*/

// JSLint options 
/*jslint white: true, funcinvoke: true, undef: true, newcap: true, nomen: true, regexp: true, bitwise: true, browser: true, forin: true, maxerr: 100, indent: 4 */

var fluid_1_5 = fluid_1_5 || {};

(function ($, fluid) {
    /***************************
     * Full Preview UI Options *
     ***************************/

    fluid.defaults("fluid.uiOptions.fullPreview", {
        gradeNames: ["fluid.uiOptions.inline"],
        container: "{fullPreview}.container",
        uiOptionsTransform: {
            config: {
                "!*.uiOptionsLoader.*.uiOptions.*.preview.*.enhancer.options": "outerPreviewEnhancerOptions"
            }
        },
        derivedDefaults: {
            templateLoader: {
                options: {
                    templates: {
                        uiOptions: "%prefix/FullPreviewUIOptions.html"
                    }
                }
            }
        }
    });
    
    fluid.uiOptions.inline.makeCreator("fluid.uiOptions.fullPreview", function (options) {
        // This is a terrible hack for FLUID-4409. Since it is impossible for us to be invoked via IoC, the only
        // source of this configuration could be the static pageEnhancer
        // The correct way to resolve the problem is to refactor UIEnhancer so that all of its configuration other than
        // the container to be bound to be enhanced is kept in a separate, shared component, "UIEnhancerConfig".
        var enhancerOptions = fluid.get(fluid, "staticEnvironment.uiEnhancer.options.originalUserOptions");
        options.outerPreviewEnhancerOptions = enhancerOptions;
        return options;
    });
    
})(jQuery, fluid_1_5);/*
Copyright 2011 OCAD University
Copyright 2011 Lucendo Development Ltd.

Licensed under the Educational Community License (ECL), Version 2.0 or the New
BSD license. You may not use this file except in compliance with one these
Licenses.

You may obtain a copy of the ECL 2.0 License and BSD License at
https://github.com/fluid-project/infusion/raw/master/Infusion-LICENSE.txt
*/

// Declare dependencies
/*global fluid_1_5:true, jQuery*/

// JSLint options 
/*jslint white: true, funcinvoke: true, undef: true, newcap: true, nomen: true, regexp: true, bitwise: true, browser: true, forin: true, maxerr: 100, indent: 4 */

var fluid_1_5 = fluid_1_5 || {};

(function ($, fluid) {
    /**********************
     * Sliding Panel *
     *********************/
     
    fluid.defaults("fluid.slidingPanel", {
        gradeNames: ["fluid.viewComponent", "autoInit"],             
        selectors: {
            panel: ".flc-slidingPanel-panel",
            toggleButton: ".flc-slidingPanel-toggleButton"
        },
        strings: {
            showText: "+ Show Display Preferences",
            hideText: "- Hide"
        },          
        events: {
            onPanelHide: null,
            onPanelShow: null,
            afterPanelHide: null,
            afterPanelShow: null
        },
        finalInitFunction: "fluid.slidingPanel.finalInit",
        invokers: {
            operateHide: "fluid.slidingPanel.slideUp",
            operateShow: "fluid.slidingPanel.slideDown"
        },
        model: {
            isShowing: false
        },
        methods: {
            showPanel: {
                finalState: true,
                name: "Show"
            },
            hidePanel: {
                finalState: false,
                name: "Hide"
            }
        }
    });
    
    fluid.slidingPanel.slideUp = function (element, callback, duration) {
        $(element).slideUp(duration || "400", callback);
    };
    
    fluid.slidingPanel.slideDown = function (element, callback, duration) {
        $(element).slideDown(duration || "400", callback);
    };
    
    fluid.slidingPanel.finalInit = function (that) {
        fluid.each(that.options.methods, function (method, methodName) {
            that[methodName] = function () {
                that.events["onPanel" + method.name].fire(that);
                that.applier.requestChange("isShowing", method.finalState);
                that.refreshView();
                that["operate" + method.name](that.locate("panel"), that.events["afterPanel" + method.name].fire);
            };
        });
        
        that.togglePanel = function () {
            that[that.model.isShowing ? "hidePanel" : "showPanel"]();
        };
        
        that.setPanelHeight = function (newHeight) {
            that.locate("panel").height(newHeight);
        };
        
        that.refreshView = function () {
            that.locate("toggleButton").text(that.options.strings[that.model.isShowing ? "hideText" : "showText"]);         
        };
    
        that.locate("toggleButton").click(that.togglePanel);        
        
        that.refreshView();
    };    

})(jQuery, fluid_1_5);
