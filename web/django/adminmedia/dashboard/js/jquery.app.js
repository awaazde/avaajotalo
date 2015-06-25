/**
 *  AD Dashboard
 *
 **/

! function($) {
    "use strict";

    function Plugin(option) {
        return this.each(function() {
            var $this = $(this),
                data = $this.data("pg.portlet"),
                options = "object" == typeof option && option;
            data || $this.data("pg.portlet", data = new Portlet(this, options)), "string" == typeof option ? data[option]() : options.hasOwnProperty("refresh") ? data.refresh(options.refresh) : options.hasOwnProperty("error") && data.error(options.error)
        })
    }
    var Portlet = function(element, options) {
        this.$element = $(element), this.options = $.extend(!0, {}, $.fn.portlet.defaults, options), this.$loader = null, this.$body = this.$element.find(".panel-body"), this.$loaderSVG = this.$loaderSVG || $('<img src="/adminmedia/dashboard/images/progress/progress-' + this.options.progress + "-" + this.options.progressColor + '.svg" style="display:none">').appendTo(this.$element)
    };
    Portlet.VERSION = "1.0.0", Portlet.prototype.collapse = function() {
        {
            var icon = this.$element.find('[data-toggle="collapse"] > i');
            this.$element.find(".panel-heading")
        }
        return this.$body.stop().slideToggle("fast"), this.$element.hasClass("panel-collapsed") ? (this.$element.removeClass("panel-collapsed"), icon.removeClass().addClass("portlet-icon sicon-angle-down"), void($.isFunction(this.options.onExpand) && this.options.onExpand())) : (this.$element.addClass("panel-collapsed"), icon.removeClass().addClass("portlet-icon sicon-angle-up"), void($.isFunction(this.options.onCollapse) && this.options.onCollapse()))
    }, Portlet.prototype.close = function() {
        this.$element.remove(), $.isFunction(this.options.onClose) && this.options.onClose()
    }, Portlet.prototype.maximize = function() {
        var icon = this.$element.find('[data-toggle="maximize"] > i');
        this.$element.hasClass("panel-maximized") ? (this.$element.removeClass("panel-maximized"), icon.removeClass("pg-fullscreen_restore").addClass("pg-fullscreen"), $.isFunction(this.options.onRestore) && this.options.onRestore()) : (this.$element.addClass("panel-maximized"), icon.removeClass("pg-fullscreen").addClass("pg-fullscreen_restore"), $.isFunction(this.options.onMaximize) && this.options.onMaximize())
    }, Portlet.prototype.refresh = function(refresh) {
        var toggle = this.$element.find('[data-toggle="refresh"]');
        if (refresh) {
            if (this.$loader && this.$loader.is(":visible")) return;
            if (!$.isFunction(this.options.onRefresh)) return;
            this.$loader = $('<div class="portlet-progress"></div>'), this.$loader.css({
                "background-color": "rgba(" + this.options.overlayColor + "," + this.options.overlayOpacity + ")"
            });
            var elem = "";
            if ("circle" == this.options.progress) elem += '<div class="progress-circle-indeterminate progress-circle-' + this.options.progressColor + '"></div>';
            else if ("bar" == this.options.progress) elem += '<div class="progress progress-small">', elem += '    <div class="progress-bar-indeterminate progress-bar-' + this.options.progressColor + '"></div>', elem += "</div>";
            else if ("circle-lg" == this.options.progress) {
                toggle.addClass("refreshing");
                var iconNew, iconOld = toggle.find("> i").first();
                toggle.find('[class$="-animated"]').length ? iconNew = toggle.find('[class$="-animated"]') : (iconNew = $("<i/>"), iconNew.css({
                    position: "absolute",
                    top: iconOld.position().top,
                    left: iconOld.position().left
                }), iconNew.addClass("portlet-icon-refresh-lg-" + this.options.progressColor + "-animated"), toggle.append(iconNew)), iconOld.addClass("fade"), iconNew.addClass("active")
            } else elem += '<div class="progress progress-small">', elem += '    <div class="progress-bar-indeterminate progress-bar-' + this.options.progressColor + '"></div>', elem += "</div>";
            this.$loader.append(elem), this.$element.append(this.$loader), this.$loader.fadeIn(), $.isFunction(this.options.onRefresh) && this.options.onRefresh()
        } else {
            var _this = this;
            this.$loader.fadeOut(function() {
                if ($(this).remove(), "circle-lg" == _this.options.progress) {
                    var iconNew = toggle.find(".active"),
                        iconOld = toggle.find(".fade");
                    iconNew.removeClass("active"), iconOld.removeClass("fade"), toggle.removeClass("refreshing")
                }
                _this.options.refresh = !1
            })
        }
    }, Portlet.prototype.error = function(error) {
        if (error) {
            var _this = this;
            this.$element.appNotification({
                style: "simple",
                message: error,
                position: "top-right",
                timeout: 0,
                type: "danger",
                onShown: function() {
                    _this.$loader.find("> div").fadeOut()
                },
                onClosed: function() {
                    _this.refresh(!1)
                }
            }).show()
        }
    };
    var old = $.fn.portlet;
    $.fn.portlet = Plugin, $.fn.portlet.Constructor = Portlet, $.fn.portlet.defaults = {
        progress: "circle",
        progressColor: "master",
        refresh: !1,
        error: null,
        overlayColor: "255,255,255",
        overlayOpacity: .8
    }, $.fn.portlet.noConflict = function() {
        return $.fn.portlet = old, this
    }, $(document).on("click.pg.portlet.data-api", '[data-toggle="collapse"]', function(e) {
        var $this = $(this),
            $target = $this.closest(".panel");
        $this.is("a") && e.preventDefault(), $target.data("pg.portlet") && $target.portlet("collapse")
    }), $(document).on("click.pg.portlet.data-api", '[data-toggle="close"]', function(e) {
        var $this = $(this),
            $target = $this.closest(".panel");
        $this.is("a") && e.preventDefault(), $target.data("pg.portlet") && $target.portlet("close")
    }), $(document).on("click.pg.portlet.data-api", '[data-toggle="refresh"]', function(e) {
        var $this = $(this),
            $target = $this.closest(".panel");
        $this.is("a") && e.preventDefault(), $target.data("pg.portlet") && $target.portlet({
            refresh: !0
        })
    }), $(document).on("click.pg.portlet.data-api", '[data-toggle="maximize"]', function(e) {
        var $this = $(this),
            $target = $this.closest(".panel");
        $this.is("a") && e.preventDefault(), $target.data("pg.portlet") && $target.portlet("maximize")
    }), $(window).on("load", function() {
        $('[data-pages="portlet"]').each(function() {
            var $portlet = $(this);
            $portlet.portlet($portlet.data())
        })
    })
}(window.jQuery),

function($) {
    "use strict";

    function Plugin(option) {
        return this.filter(":input").each(function() {
            var $this = $(this),
                data = $this.data("app.circularProgress"),
                options = "object" == typeof option && option;
            data || $this.data("app.circularProgress", data = new Progress(this, options)), "string" == typeof option ? data[option]() : options.hasOwnProperty("value") && data.value(options.value)
        })
    }

    function perc2deg(p) {
        return parseInt(p / 100 * 360)
    }
    var Progress = function(element, options) {
        this.$element = $(element), this.options = $.extend(!0, {}, $.fn.circularProgress.defaults, options), this.$container = $('<div class="progress-circle"></div>'), this.$element.attr("data-color") && this.$container.addClass("progress-circle-" + this.$element.attr("data-color")), this.$element.attr("data-thick") && this.$container.addClass("progress-circle-thick"), this.$pie = $('<div class="pie"></div>'), this.$pie.$left = $('<div class="left-side half-circle"></div>'), this.$pie.$right = $('<div class="right-side half-circle"></div>'), this.$pie.append(this.$pie.$left).append(this.$pie.$right), this.$container.append(this.$pie).append('<div class="shadow"></div>'), this.$element.after(this.$container), this.val = this.$element.val();
        var deg = perc2deg(this.val);
        this.val <= 50 ? this.$pie.$right.css("transform", "rotate(" + deg + "deg)") : (this.$pie.css("clip", "rect(auto, auto, auto, auto)"), this.$pie.$right.css("transform", "rotate(180deg)"), this.$pie.$left.css("transform", "rotate(" + deg + "deg)"))
    };
    Progress.VERSION = "1.0.0", Progress.prototype.value = function(val) {
        if ("undefined" != typeof val) {
            var deg = perc2deg(val);
            this.$pie.removeAttr("style"), this.$pie.$right.removeAttr("style"), this.$pie.$left.removeAttr("style"), 50 >= val ? this.$pie.$right.css("transform", "rotate(" + deg + "deg)") : (this.$pie.css("clip", "rect(auto, auto, auto, auto)"), this.$pie.$right.css("transform", "rotate(180deg)"), this.$pie.$left.css("transform", "rotate(" + deg + "deg)"))
        }
    };
    var old = $.fn.circularProgress;
    $.fn.circularProgress = Plugin, $.fn.circularProgress.Constructor = Progress, $.fn.circularProgress.defaults = {
        value: 0
    }, $.fn.circularProgress.noConflict = function() {
        return $.fn.circularProgress = old, this
    }, $(window).on("load", function() {
        $('[data-pages-progress="circle"]').each(function() {
            var $progress = $(this);
            $progress.circularProgress($progress.data())
        })
    })
}(window.jQuery),

function($) {
    "use strict";

    /**
    Sidebar Module
    */
    var SideBar = function() {
        this.$body = $("body"),
        this.$sideBar = $('aside.left-panel'),
        this.$navbarToggle = $(".navbar-toggle"),
        this.$navbarItem = $("aside.left-panel nav.navigation > ul > li:has(ul) > a")
    };

    //initilizing 
    SideBar.prototype.init = function() {
        //on toggle side menu bar
        var $this = this;
        $(document).on('click', '.navbar-toggle', function () {
            $this.$sideBar.toggleClass('collapsed');
        }); 

        //on menu item clicking
        this.$navbarItem.click(function () {
            if ($this.$sideBar.hasClass('collapsed') == false || $(window).width() < 768) {
                $("aside.left-panel nav.navigation > ul > li > ul").slideUp(300);
                $("aside.left-panel nav.navigation > ul > li").removeClass('active');
                if (!$(this).next().is(":visible")) {
                    $(this).next().slideToggle(300, function () {
                        $("aside.left-panel:not(.collapsed)").getNiceScroll().resize();
                    });
                    $(this).closest('li').addClass('active');
                }
                return false;
            }
        });

        //adding nicescroll to sidebar
        if ($.isFunction($.fn.niceScroll)) {
            $("aside.left-panel:not(.collapsed)").niceScroll({
                cursorcolor: '#8e909a',
                cursorborder: '0px solid #fff',
                cursoropacitymax: '0.5',
                cursorborderradius: '0px'
            });
        }
    },

    //exposing the sidebar module
    $.SideBar = new SideBar, $.SideBar.Constructor = SideBar
    
}(window.jQuery),


function($) {
    "use strict";
	
    var Graph = function() {
    	this.$callsInGraph = null
    };
    
    Graph.prototype.init = function() {
    	
    	
    }, 
    
    Graph.prototype.getColor = function(color, opacity) {
        opacity = parseFloat(opacity) || 1;
        var elem = $(".pg-colors").length ? $(".pg-colors") : $('<div class="pg-colors"></div>').appendTo("body"),
            colorElem = elem.find('[data-color="' + color + '"]').length ? elem.find('[data-color="' + color + '"]') : $('<div class="bg-' + color + '" data-color="' + color + '"></div>').appendTo(elem),
            color = colorElem.css("background-color"),
            rgb = color.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/),
            rgba = "rgba(" + rgb[1] + ", " + rgb[2] + ", " + rgb[3] + ", " + opacity + ")";
        return rgba
    },
    
     Graph.prototype.call_count_zoom_line_chart = function(chart_json_data,div_id,chart_display_id) {
    	
    	$(div_id).show();
    	var in_bound_call_count_data = [];
    	var date = [];
    	var inbound = chart_json_data.inbound_call_count;
    	var outbound_dial = chart_json_data.outbound_dial_call_count;
    	var outbound_pickup = chart_json_data.outbound_pickup_call_count;
    	
    	$.each(inbound.data, function(key, value) {
    		in_bound_call_count_data.push(parseInt(value));
    		date.push(key);
    	});  
    	
    	var out_bound_dial_call_count_data = [];
    	$.each(outbound_dial.data, function(key, value) {
    		out_bound_dial_call_count_data.push(parseInt(value));
    	});  
    	
    	var out_bound_pickup_call_count_data = [];
    	$.each(outbound_pickup.data, function(key, value) {
    		out_bound_pickup_call_count_data.push(parseInt(value));
    	});  
    	
    	
    	var string_data = "Date,Inbound Calls, Dial Calls, Pickup Calls\n";
    	var $this = this;
    	for (var i=0; i < in_bound_call_count_data.length; i++ )
    	{
    		string_data = string_data + date[i] +"," + in_bound_call_count_data[i]+ "," + out_bound_dial_call_count_data[i];
    		string_data = string_data + " , " + out_bound_pickup_call_count_data[i] + "\n";

    	}
    
    	var g = new Dygraph(document.getElementById(chart_display_id),string_data,{
            // options go here. See http://dygraphs.com/options.html
    		
    		animatedZooms : true,
    	    title: 'CALL COUNT',
            xlabel: 'Date',
            ylabel: 'Minutes',
            colors : ["#fd7037", "#333b4d", "#337ab7"],
            highlightCircleSize : 7,
            
        });
    	return g;
    	
    },
    
    Graph.prototype.recharge_line_chart = function(chart_json_data,div_id,chart_display_id,graph_name) {
    	$(div_id).show(chart_json_data);
    	
    	var date = [];
    	var recharge = [];
    	$.each(chart_json_data.data, function(key, value) {
    		recharge.push(parseInt(value));
    		date.push(key);
    	});  
    	
    	var string_data = "Date," + chart_json_data["key"] +"\n";
    	var $this = this;
    	for (var i=0; i < recharge.length; i++ )
    	{
    		string_data = string_data + date[i] +"," + recharge[i]+ "\n";

    	}
    
    	var g = new Dygraph(document.getElementById(chart_display_id),string_data,{
            // options go here. See http://dygraphs.com/options.html
    		
    		animatedZooms : true,
    	    title: graph_name,
            xlabel: 'Date',
            ylabel: 'Rupess',
            colors : ["#fd7037"],
            highlightCircleSize : 7,
            
        });
    	return g;
    	
    },
    
    Graph.prototype.single_line_chart = function(chart_json_data,div_id,chart_display_id,graph_name) {
    	$(div_id).show();
    	
    	var data = [];
    	var hour = [];
    	for (var i = 0; i<24;i++)
    	{
    		if(chart_json_data["data"].hasOwnProperty(i)){
    			data.push(chart_json_data["data"][i])
    		}
    		else
    		{
    			data.push(0);
    		}
    		
    		hour.push(i);
    	}
    	
    	var string_data = "Hour,"+chart_json_data["key"]+"\n";
    	var $this = this;
    	for (var i=0; i < hour.length; i++ )
    	{
    		string_data = string_data +  hour[i] +", " +  data[i] + "\n";

    	}
    
    	var g = new Dygraph(document.getElementById(chart_display_id),string_data,{
            // options go here. See http://dygraphs.com/options.html
    		animatedZooms : false,
    		height : "95%",
    		width : "95%",
    	    title: graph_name,
            xlabel: 'Hour',
            ylabel: 'Call Count',
            colors : ["#fd7037"],
            highlightCircleSize : 7,
            interactionModel : null,
            
            
        });
    	return g;
    	
    },
    
    
    
    Graph.prototype.double_line_chart = function( total_dial_call,total_pickup_call,div_id,chart_display_id,graph_name) {
    	$(div_id).show();
    	var dial_call_data = [];
     	var pickup_call_data = [];
     	var hour = [];
     	
     	
     	for (var i = 0; i<24;i++)
    	{
    		if(total_dial_call["data"].hasOwnProperty(i)){
    			dial_call_data.push(total_dial_call["data"][i])
    		}
    		else
    		{
    			dial_call_data.push(0);
    		}
    		
    		if(total_pickup_call["data"].hasOwnProperty(i)){
    			pickup_call_data.push(total_pickup_call["data"][i])
    		}
    		else
    		{
    			pickup_call_data.push(0);
    		}
    		
    		hour.push(i);
    	}
     	
     	var string_data = "Hour,"+total_dial_call["key"]+ "," +total_pickup_call["key"] + "\n";
    	var $this = this;
    	for (var i=0; i < hour.length; i++ )
    	{
    		string_data = string_data + hour[i] +","+ dial_call_data[i] +", " +  pickup_call_data[i] +"\n";

    	}
    
    	var g = new Dygraph(document.getElementById(chart_display_id),string_data,{
            // options go here. See http://dygraphs.com/options.html
    		animatedZooms : false,
    		height : "95%",
    		width : "95%",
    	    title: graph_name,
            xlabel: 'Hour',
            ylabel: 'Call Count',
            colors : ["#fd7037",  "#333b4d"],
            highlightCircleSize : 7,
            interactionModel : null,
        });
    	return g;
},

    
    
    
    
    
    Graph.prototype.minute_used_zoom_line_chart = function(chart_json_data,div_id,chart_display_id) {
    	$(div_id).show();
    	var in_bound_minute_used_data = [];
    	var date = [];
    	var inbound = chart_json_data.inbound_minute_used;
    	var outbound = chart_json_data.outbound_minute_used;
    	
    	
    	$.each(inbound.data, function(key, value) {
    		in_bound_minute_used_data.push(parseInt(value)/60);
    		date.push(key);
    	});  
    	
    	var out_bound_minute_used_data = [];
    	$.each(outbound.data, function(key, value) {
    		out_bound_minute_used_data.push(parseInt(value)/60);
    	});  
    	    
    	var string_data = "Date,Outbound Minute, Inbound Minute, Total Minute\n";
    	var $this = this;
    	for (var i=0; i < in_bound_minute_used_data.length; i++ )
    	{
    		string_data = string_data + date[i] +"," + out_bound_minute_used_data[i]+ "," + in_bound_minute_used_data[i];
    		string_data = string_data + " , " + (out_bound_minute_used_data[i]+in_bound_minute_used_data[i]) + "\n";

    	}
    
    	var g = new Dygraph(document.getElementById(chart_display_id),string_data,{
            // options go here. See http://dygraphs.com/options.html
    		
    		animatedZooms : true,
    	    title: 'Total Minute Used',
            xlabel: 'Date',
            ylabel: 'Minutes',
            colors : ["#fd7037", "#333b4d", "#337ab7"],
            highlightCircleSize : 7,
            
        });
    	return g;
    	
    },
  
    Graph.prototype.bar_chart = function(chart_json_data,div_id){
    	$(div_id).show();
    	var $this = this;
    	var chart_data = chart_json_data.data
    	var key = chart_json_data.key
    	var data1 = [];
    	$.each(chart_data, function(key, value) {
    		var myObject = new Object();
    		myObject.label = key;
    		myObject.value = value;
    	    data1.push(myObject);
    	});
    	
    	var finaldata = new Object();
    	finaldata.key = key
	    finaldata.values = data1;
    	
	    var final_graph_data = [];
	    final_graph_data.push(finaldata);
	    $(".widget-calls-in-chart svg").empty();
	    
	    var tooltip = function(key, x, y, e, graph) {
	        return '<br/> <h3> Second : ' + key + '</h3>' +
	               '<p> Count' +  y + '</p>';
	    };
	    
    	nv.addGraph(function() {
    		  var chart = nv.models.discreteBarChart()
    		      .x(function(d) { return d.label })    //Specify the data accessors.
    		      .y(function(d) { return d.value })
    		      .staggerLabels(true)    //Too many bars and not enough room? Try staggering labels.
    		      .tooltips(tooltip)        //Don't show tooltips
    		      .showValues(true);    //...instead, show the bar value right on top of each bar.
    		
    		  chart.yAxis.axisLabel("Call Counts");
    		  chart.xAxis.axisLabel("Seconds");
    		  
    		  d3.select(div_id +'> svg').datum(final_graph_data).call(chart);
  		    
    		  nv.utils.windowResize(chart.update);
    		  
  		    $(div_id).data('chart', chart);
      		$this.$callsInGraph = chart; 
      		return chart;
    		});
    }
    
    
    Graph.prototype.pie_chart = function(chart_json_data,div_id){
    	$(div_id).show();
    	
    	var $this = this;
    	var chart_data = chart_json_data["data"];
    	var key = chart_json_data["key"];
    		var data1 = [];
    		
    		if (chart_data != null ) {
    		
        	$.each(chart_data, function(key, value) {
        		var myObject = new Object();
        		myObject.label = key;
        		myObject.value = value;
        	    data1.push(myObject);
        	});
        	
    		}
        	
        	$(".widget-calls-in-chart svg").empty();
    	nv.addGraph(function() {
    		  var chart = nv.models.pieChart()
    		      .x(function(d) { return d.label })
    		      .y(function(d) { return d.value })
    		      .showLabels(true)     //Display pie labels
    		      .labelThreshold(.05)  //Configure the minimum slice size for labels to show up
    		      .labelType("percent") //Configure what type of data to show in the label. Can be "key", "value" or "percent"
    		      .donut(true)          //Turn on Donut mode. Makes pie chart look tasty!
    		      .donutRatio(0.35)     //Configure how big you want the donut hole size to be.
    		      ;

    		    
    		  	 
    		  d3.select(div_id +'> svg').datum(data1).transition().duration(350).call(chart);
    		    
    		    $(div_id).data('chart', chart);
        		$this.$callsInGraph = chart; 
        		return chart;
    		 
    		});
    },
    
     
    $.Graph = new Graph, $.Graph.Constructor = Graph
    
}(window.jQuery),

function($) {
    "use strict";
	
    var UserSettingPage = function() {
        this.$body = $("body"),
        this.$usersearchBox = $("#user-setting-search"),
        this.$settingsURL = $("#settings-url"),
        this.$errorContainer = $("#show-notification")
    };
    
    UserSettingPage.prototype.init = function() {
    	var $this = this;
    	$.fn.select2 && $this.$usersearchBox.select2({}).on("select2-opening", function() {
                $.fn.scrollbar && $(".select2-results").scrollbarda({
                    ignoreMobile: !1
                })
           });
    	
    	$this.$usersearchBox.on("change", function(e) {
    		var url = $this.$settingsURL.val() + $(this).val() + '/';
    		
    		//clearning localstorage
    		localStorage.clear();
    		$(location).attr('href',url);
    	}); 
    	
    	//checking if any error occurred
    	if($this.$errorContainer.length > 0) {
    		var type = $this.$errorContainer.attr('data-type');
    		var msg = $this.$errorContainer.attr('data-message'); 
    		
    		
    	
    	}
    	
    	//removing - hack
    	$("#s2id_ac-group-select").removeClass('form-control');
    }, 
    $.UserSettingPage = new UserSettingPage, $.UserSettingPage.Constructor = UserSettingPage
    
}(window.jQuery),

function($) {
    "use strict";
	
    var AddCouponPage = function() {
        this.$body = $("body");
        this.$selectUser = $("#id_user");
    };
    
    AddCouponPage.prototype.init = function() {
    	
    	var $this = this;
    	
     	$.fn.select2 && $this.$selectUser.select2({}).on("select2-opening", function() {
            $.fn.scrollbar && $(".select2-results").scrollbar({
                ignoreMobile: !1
            })
       });
     	
     	$("#s2id_id_user").removeClass('form-control');
     	$("#s2id_id_user").addClass('width-100');
    	
    }, 
    
    $.AddCouponPage = new AddCouponPage, $.AddCouponPage.Constructor = AddCouponPage
    
}(window.jQuery),

function($) {
    "use strict";
    
    var ReportPage = function() {
    	
        this.$body = $("body"),
        
        this.$userselect = $("#select-user"),
        this.$groupselect = $("#select-group"),
        this.$broadcastselect = $("#select-broadcast"),
        
        this.$select_user_div = $("#select-user-div"),
        this.$select_group_div = $("#select-group-div"),
        this.$select_broadcast_div = $("#select-broadcast-div"),
        
        this.$graph_pickup = $("#call_vs_pickup"),
        this.$graph_call_in = $("#call_in"),
        this.$graph_forward = $("#forward"),
        this.$graph_response = $("#response"),
        this.$graph_attend_wise_pickup = $("#attend_wise_pickup"),
        this.$graph_call_duration = $("#call_duration"),
        this.$graph_total_minute_used = $("#total_minute_used"),
        this.$graph_total_call_count = $("#total_call_count"),
        this.$graph_credit_used = $("#credit_used"),
        this.$graph_recharge = $("#recharge"),
        
        this.$start_date = $("#startdate"),
        this.$end_date = $("#enddate"),
        this.$graph_type= $("#graph_type"),
        
        this.$chart_data_for_csv = $("#chart_data_for_csv"),
        
        this.$widget_calls_in_chart = $("#widget-calls-in-chart"),
        this.$widget_calls_forward_chart = $("#widget-calls-forward-chart"),
        this.$widget_calls_dial_vs_pickup_chart = $("#widget-calls-dial-vs-pickup-chart"),
        this.$widget_attempt_wise_pickup_chart = $("#widget-attempt-wise-pickup-chart"),
        this.$widget_call_response_chart = $("#widget-call-response-chart"),
        this.$widget_call_duration_chart = $("#widget-call-duration-chart"),
        this.$widget_total_minute_used_chart = $("#widget-total-minute-used-chart"),
        this.$widget_credit_used_chart = $("#widget-credit-used-chart"),
        this.$widget_recharge_chart = $("#widget-recharge-chart"),
        this.$widget_total_call_count_chart = $("#widget-total-call-count-chart"),
        
        
        this.$get_graph_btn = $("#get_graph_btn"),
        this.$save_as_csv_btn = $("#save_as_csv_btn"),
        this.$graph_menu = $("#graph_menu"),
        
        this.selected_user,
        this.selected_group,
        this.selected_broadcast,
        
        this.visible,
        this.chart_list
        this.graph_url_data;
    };
    
    ReportPage.prototype.set_graph_urls = function(data)
    {
    	var $this = this;
    	this.graph_url_data = data;
    	
    	if($(".user-select-c").length > 0)
    	{
    		console.log("");
    	}
    	else
    	{
    		
    		$.ReportPage.select_user_event($this.$userselect.val());
    		$this.$select_group_div.show();
    	}
    	this.$get_graph_btn.trigger('click');
    }
  
    ReportPage.prototype.set_visible_level = function(visible_level) {
    	this.visible = visible_level;
    }
    
    
    ReportPage.prototype.set_user_id = function(user_id) {
    	this.selected_user = user_id;
    }
    
    ReportPage.prototype.set_group_id = function(group_id) {
    	this.selected_group = group_id;
    }
    
    ReportPage.prototype.set_broadcast_id = function(broadcast_id) {
    	this.selected_broadcast = broadcast_id;
    }
    
    ReportPage.prototype.JSONToCSVConvertor = function(JSONData, ReportTitle, ShowLabel) {
        //If JSONData is not an object then JSON.parse will parse the JSON string in an Object
        //var arrData = typeof JSONData != 'object' ? JSON.parse(JSONData) : JSONData;
    	var arrData = jQuery.parseJSON(JSONData);
    	
        var CSV = '';
        //Set Report title in first row or line

        CSV  = ReportTitle + '\r\n\n';
        
        var data_array = [];
        var first_column = [];
        //This condition will generate the Label/Header
        	
            var row = arrData["group_by_on"]+",";

            //This loop will extract the label from 1st index of on array
            for (var key in arrData)
            {
            	if (key != "group_by_on")
            	{
	            	var firstJsonObject = arrData[key];
	            	var colum_array = [];
	            	for (var key in firstJsonObject)
	            	{
	            		
	            		if(key=="key")
	            		{
	            			row = row + firstJsonObject[key] + ",";
	            		}
	            		if(key=="data")
	            		{
	      
	            			var each_row = firstJsonObject[key];
	            			
	            			for (var key in each_row)
	            			{
	            				
	            				colum_array.push(each_row[key]);
	            			}
	            			
	            			if (first_column.length == 0)
	            			{
	            				for (var key in each_row)
	                			{
	            					first_column.push(key);
	                  			}
	            			}
	            		}	
	            	}
            	
	            	data_array.push(colum_array);
            	}
            }
            
            row = row.slice(0, -1);
            CSV = CSV + row + '\r\n';
            
           
            for (var i = 0; i < first_column.length; i++) 
            {
                var row = first_column[i] + ",";
                for (var j=0; j < data_array.length; j++) 
                {
                	row = row + data_array[j][i] + ",";
                }
                row = row.slice(0, -1);
                CSV = CSV + row + '\r\n';
            }

        
        
        if (CSV == '') {
            alert("Invalid data");
            return;
        }

        //Generate a file name
        var fileName = "MyReport_";
        //this will remove the blank-spaces from the title and replace it with an underscore
        fileName  = ReportTitle.replace(/ /g, "_");

        //Initialize file format you want csv or xls
        var uri = 'data:text/csv;charset=utf-8,' +  escape(CSV);

        // Now the little tricky part.
        // you can use either>> window.open(uri);
        // but this will not work in some browsers
        // or you will not get the correct file extension    

        //this trick will generate a temp <a /> tag
        var link = document.createElement("a");
        link.href = uri;

        //set the visibility hidden so it will not effect on your web-layout
        //link.style = "visibility:hidden";
        link.download = fileName + ".csv";

        //this part will append the anchor tag and remove it after automatic click
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
    }
    
    
    ReportPage.prototype.hide_all_graph = function() {
		this.$widget_calls_in_chart.hide();
	    this.$widget_calls_forward_chart.hide();
	    this.$widget_calls_dial_vs_pickup_chart.hide();
	    this.$widget_attempt_wise_pickup_chart.hide();
	    this.$widget_call_response_chart.hide();
	    this.$widget_call_duration_chart.hide();
	    this.$widget_total_minute_used_chart.hide();
	    this.$widget_credit_used_chart.hide();
	    this.$widget_recharge_chart.hide();
	    this.$widget_total_call_count_chart.hide();
	}
    
    ReportPage.prototype.show_error = function(error){
    	
    	$("#success-alert").empty();
		if (error.status == 403)
		{
			$("#success-alert").append("<p> You are not allowed to access this data. </p>");
			$("#success-alert").fadeTo(6000, 500).slideUp(500, function(){
				$("#success-alert").alert('close');
			});
		}
		else
		{
			$("#success-alert").append("<p> Somthing want wrong please try again or contact our support </p>");
			$("#success-alert").fadeTo(6000, 500).slideUp(500, function(){
				$("#success-alert").alert('close');
			});
		}
    	
    }
    
    ReportPage.prototype.get_dial_vs_pickup_graph = function(chart_id) {
    	
    	$.ReportPage.hide_all_graph();
        
        var $this = this;
    	
        $.ajax({
        		url: $this.graph_url_data["report"], 
				method: "POST", 
	
				data : 
				{'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(), selected_user : $this.selected_user, selected_group : $this.selected_group,
				selected_broadcast : $this.selected_broadcast, graph : chart_id, start_date : $this.$start_date.val(), end_date : $this.$end_date.val() 
				},
				
				success: function (response) 
				{
					var graph_data = response;
					$.Graph.init();
					var export_data = JSON.stringify(response);
					$this.$chart_data_for_csv.val(export_data);
					$.Graph.double_line_chart(graph_data.total_dial_call,graph_data.total_pickup_call,$this.$widget_calls_dial_vs_pickup_chart.selector, "widget-calls-dial-vs-pickup-chart","Attempts vs. Pickup over time");
				},
				error: function(xhr)
				{	
					$.ReportPage.show_error(xhr);
					
			    },
				dataType: 'json',	
			});
    }
    
    ReportPage.prototype.get_call_in_graph = function(chart_id)
    {
    	$.ReportPage.hide_all_graph();
        
    	var $this = this;
    	
    	$.ajax({
    			url: $this.graph_url_data["report"],
				method: "POST",
				
				data :
				{'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(), selected_user : $this.selected_user, 
				selected_group : $this.selected_group, selected_broadcast : $this.selected_broadcast, graph : chart_id, start_date : $this.$start_date.val(), end_date : $this.$end_date.val() 
				},
  	
				success: function (response) 
				{
					
					var graph_data = response;
					
					$.Graph.init();
					var export_data = JSON.stringify(response);
					$this.$chart_data_for_csv.val(export_data);
					$.Graph.single_line_chart(graph_data.call_in,$this.$widget_calls_in_chart.selector,"widget-calls-in-chart","Call-In over time");
  		
				},
				error: function(xhr)
				{	
					$.ReportPage.show_error(xhr);
					
			    },
				dataType: 'json',
			});
    }
    
    ReportPage.prototype.get_forward_graph = function(chart_id)
    {
    	
    	$.ReportPage.hide_all_graph();
    	
    	var $this = this;
    	$.ajax({
    			url: $this.graph_url_data["report"],
				method: "POST",
				data : 
				{'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(), selected_user : $this.selected_user, 
				selected_group : $this.selected_group, selected_broadcast : $this.selected_broadcast, graph : chart_id, start_date : $this.$start_date.val(), end_date : $this.$end_date.val() 
				},
  		
				success: function (response) 
				{
					var graph_data = response;
					
					$.Graph.init();
					var export_data = JSON.stringify(response);
					$this.$chart_data_for_csv.val(export_data);
					$.Graph.single_line_chart(graph_data.forward,$this.$widget_calls_forward_chart.selector,"widget-calls-forward-chart","Call Forward over time");
  		
				},
				error: function(xhr)
				{	
					$.ReportPage.show_error(xhr);
					
			    },
				dataType: 'json',
			});
    }
    
    ReportPage.prototype.get_attend_wise_pickup_graph = function(chart_id)
    {
    	$.ReportPage.hide_all_graph();
    	var $this = this;
    	$.ajax({
    			url: $this.graph_url_data["report"],
				method: "POST",
				data : 
				{'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(), selected_user : $this.selected_user, 
				selected_group : $this.selected_group, selected_broadcast : $this.selected_broadcast, graph : chart_id, start_date : $this.$start_date.val(), end_date : $this.$end_date.val() 
				},
  	
				success: function (response) 
				{
	  		
					var graph_data = response;

					$.Graph.init();
					var export_data = JSON.stringify(response);
					$this.$chart_data_for_csv.val(export_data);
					$.Graph.pie_chart(graph_data.attemp_wise_pickup,$this.$widget_attempt_wise_pickup_chart.selector);
				},
				error: function(xhr)
				{	
					$.ReportPage.show_error(xhr);
					
			    },
				dataType: 'json',	
			});
	}
    
    ReportPage.prototype.get_call_duration_graph = function(chart_id)
    {
    	$.ReportPage.hide_all_graph();
    	
    	var $this = this;
    	$.ajax({
    			url: $this.graph_url_data["report"],
				method: "POST",
				data :
				{'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(), selected_user : $this.selected_user, 
				selected_group : $this.selected_group, selected_broadcast : $this.selected_broadcast, graph : chart_id, start_date : $this.$start_date.val(), end_date : $this.$end_date.val() 
				},
  	
				success: function (response) 
				{
		  		
					var graph_data = response;

					$.Graph.init();
					var export_data = JSON.stringify(response);
					$this.$chart_data_for_csv.val(export_data);
					$.Graph.bar_chart(graph_data.duration,$this.$widget_call_duration_chart.selector);
		  		},
				error: function(xhr)
				{	
					$.ReportPage.show_error(xhr);
					
			    },
			dataType: 'json',	
		});
	}

    ReportPage.prototype.get_response_graph = function(chart_id)

    {
    	$.ReportPage.hide_all_graph();
    	
    	var $this = this;
    	 
    	$.ajax({
    			url: $this.graph_url_data["report"],
				method: "POST",
				data : 
				{'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(), selected_user : $this.selected_user, 
    			selected_group : $this.selected_group, selected_broadcast : $this.selected_broadcast, graph : chart_id, start_date : $this.$start_date.val(), end_date : $this.$end_date.val() 
				},
    	
				success: function (response) 
				{
    		
					var graph_data = response;

					$.Graph.init();
					var export_data = JSON.stringify(response);
					$this.$chart_data_for_csv.val(export_data);
					$.Graph.pie_chart(graph_data.response_graph,$this.$widget_call_response_chart.selector);
			 
				},
				error: function(xhr)
				{	
					$.ReportPage.show_error(xhr);
					
			    },dataType: 'json',	
			});
    
	}

    ReportPage.prototype.get_total_call_count_graph = function(chart_id)
    {
    	
    	$.ReportPage.hide_all_graph();
        
    	var $this = this;
    	$this.$widget_total_call_count_chart.show();
    	
    	$.ajax({
    			url: $this.graph_url_data["report"],
				method: "POST",
				data : 
				{'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(), selected_user : $this.selected_user, 
    			selected_group : $this.selected_group, selected_broadcast : $this.selected_broadcast, graph : chart_id, start_date : $this.$start_date.val(), end_date : $this.$end_date.val() 
				},
    	
				success: function (response) 
				{
					var graph_data = response;
					$.Graph.init();
					var export_data = JSON.stringify(response);
					$this.$chart_data_for_csv.val(export_data);
					$.Graph.call_count_zoom_line_chart(graph_data,$this.$widget_total_call_count_chart.selector,"widget-total-call-count-chart");
				},
				error: function(xhr)
				{	
					$.ReportPage.show_error(xhr);
					
			    },dataType: 'json',	
			});
	}
   

    
    ReportPage.prototype.get_total_minute_used_graph = function(chart_id)
    {

        $.ReportPage.hide_all_graph();
        
    	var $this = this;
    	 
    	$this.$widget_total_minute_used_chart.show();
    	
    	$.ajax({
    			url: $this.graph_url_data["report"],
				method: "POST",
				data : 
				{'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(), selected_user : $this.selected_user, 
    			selected_group : $this.selected_group, selected_broadcast : $this.selected_broadcast, graph : chart_id, start_date : $this.$start_date.val(), end_date : $this.$end_date.val() 
				},
    	
				success: function (response) 
				{
					var graph_data = response;
					var export_data = JSON.stringify(response);
					$this.$chart_data_for_csv.val(export_data); 
					$.Graph.minute_used_zoom_line_chart(graph_data,$this.$widget_total_minute_used_chart.selector,"widget-total-minute-used-chart");
				},
				error: function(xhr)
				{	
					$.ReportPage.show_error(xhr);
					
			    },dataType: 'json',	
			});
	}
   

    ReportPage.prototype.get_recharge_graph = function(chart_id)

    {

        $.ReportPage.hide_all_graph();
    	var $this = this;
    	 
    	$this.$widget_recharge_chart.show();
    	
    	$.ajax({
    			url: $this.graph_url_data["report"],
				method: "POST",
				data : 
				{'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(), selected_user : $this.selected_user, 
    			selected_group : $this.selected_group, selected_broadcast : $this.selected_broadcast, graph : chart_id, start_date : $this.$start_date.val(), end_date : $this.$end_date.val() 
				},
    	
				success: function (response) 
				{
					var graph_data = response;
					$.Graph.init();
					var export_data = JSON.stringify(response);
					$this.$chart_data_for_csv.val(export_data);
					$.Graph.recharge_line_chart(graph_data.recharge,$this.$widget_recharge_chart.selector,"widget-recharge-chart","Recharge Graph");
					
				},
				error: function(xhr)
				{	
					$.ReportPage.show_error(xhr);
					
			    },dataType: 'json',	
			});
    
	}
    
    ReportPage.prototype.set_graph_menu = function (graph_menu) {
     	var $this = this;
       	$this.$graph_type.val("");
    	var append_options = "";
        	$.each(graph_menu, function(key, value) {
        		if ($this.$graph_type.val() == "")
        		{
        			$this.$graph_type.val(key);
        		}
        		append_options = append_options + '<li><a id='+key+' href="" >';
        		append_options = append_options + value;
        		append_options = append_options + '</a></li> ';
        	});
        
        this.$graph_menu.empty().append(append_options);
    }
    
    ReportPage.prototype.set_options = function (option_data,select_tag_id){ 
   
    	var append_options = '<option></option>';
    	
    	$.each(option_data, function(key, value) {	
    	
    		append_options = append_options + '<option id='+key+' value='+key+'> ';
    		append_options = append_options + value;
    		append_options = append_options + '</option> ';
    	});
    	$(select_tag_id).empty().append(append_options);
    	$(select_tag_id).select2("val", "---");
    	
    	this.$get_graph_btn.trigger('click');	
    }
    
    ReportPage.prototype.select_broadcast_event = function(broadcast_id) {
        
    	$.ReportPage.set_broadcast_id (broadcast_id);
    	var $this = this;
    	
    	$.ajax({
    		url: $this.graph_url_data["report"],
			method: "POST",
			data : 
			{'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(), selected_user : $this.selected_user, 
			selected_group : $this.selected_group, selected_broadcast : $this.selected_broadcast , select_broadcast : "True"
			},
	
			complete: function (response) 
			{
				var group_data = response;
				$.ReportPage.set_graph_menu(group_data.visible_graph_data);
		 
			},dataType: 'json',	
		});
    	$this.$get_graph_btn.trigger('click');

    }
    
    ReportPage.prototype.select_group_event = function(group_id) {
    	
    	$.ReportPage.set_group_id (group_id);
    	$.ReportPage.set_broadcast_id ("");
    	var $this = this;
    	
    	$.ajax({
    		url: $this.graph_url_data["report"],
			method: "POST",
			data : 
			{'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(), selected_user : $this.selected_user, 
			selected_group : $this.selected_group, selected_broadcast : $this.selected_broadcast , select_group : "True"
			},
			success: function (response) 
			{
				var broadcast_data = response;
				$.ReportPage.set_options(broadcast_data.broadcast_data,$this.$broadcastselect.selector)
				$.ReportPage.set_graph_menu(broadcast_data.visible_graph_data);
		 
			},
			error: function(xhr)
			{	
				$.ReportPage.show_error(xhr);
				
		    },
			dataType: 'json',
		});
    }
    
    ReportPage.prototype.select_user_event = function(user_id) {
    	
    	$.ReportPage.set_user_id (user_id);
    	$.ReportPage.set_group_id ("");
    	$.ReportPage.set_broadcast_id ("");
    	var $this = this;
    	
    	$.ajax({
    		url: $this.graph_url_data["report"],
			method: "POST",
			data : 
			{'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(), selected_user : $this.selected_user, 
			selected_group : $this.selected_group, selected_broadcast : $this.selected_broadcast , select_user : "True"
			},
			success: function (response) 
			{
				var group_data = response;
				$.ReportPage.set_options(group_data.group_data,$this.$groupselect.selector)
				$.ReportPage.set_graph_menu(group_data.visible_graph_data);
			},
			error: function(xhr)
			{	
				$.ReportPage.show_error(xhr);
				
		    },dataType: 'json',	
		});
    	
    }
    
    ReportPage.prototype.init = function() {
     	var $this = this;
     	$.ReportPage.hide_all_graph();
     	
     	if($(".user-select-c").length > 0) {
	     	$.fn.select2 && $this.$userselect.select2({}).on("select2-opening", function() {
	            $.fn.scrollbar && $(".select2-results").scrollbar({
	                ignoreMobile: !1
	            })
	       });
     	}
     	
     	
     	$.fn.select2 && $this.$groupselect.select2({}).on("select2-opening", function() {
            $.fn.scrollbar && $(".select2-results").scrollbar({
                ignoreMobile: !1
            })
       });
    	
     	$.fn.select2 && $this.$broadcastselect.select2({}).on("select2-opening", function() {
            $.fn.scrollbar && $(".select2-results").scrollbar({
                ignoreMobile: !1
            })
       });
     	
     	this.$get_graph_btn.click(function () {
     		var chart_id = $this.$graph_type.val();
     		if (chart_id == 'call_in'){
     			$.ReportPage.get_call_in_graph(chart_id);
     		}else if (chart_id == 'call_duration'){
     			$.ReportPage.get_call_duration_graph(chart_id);
     		}else if (chart_id == 'forward'){
     			$.ReportPage.get_forward_graph(chart_id);
     		}else if (chart_id == 'attend_wise_pickup'){
     			$.ReportPage.get_attend_wise_pickup_graph(chart_id);
     		}else if (chart_id == 'call_vs_pickup'){
     			$.ReportPage.get_dial_vs_pickup_graph(chart_id);
     		}else if (chart_id == 'response'){
     			$.ReportPage.get_response_graph(chart_id);
     		}else if (chart_id == 'total_minute_used'){
     			$.ReportPage.get_total_minute_used_graph(chart_id);
     		}else if (chart_id == 'total_call_count'){
     			$.ReportPage.get_total_call_count_graph(chart_id);
     		}else if (chart_id == 'recharge'){
     			$.ReportPage.get_recharge_graph(chart_id);
     		}else {
     			$.ReportPage.get_total_minute_used_graph("total_minute_used");
     		}
     	});
     	
     	this.$save_as_csv_btn.click(function () {
     		$.ReportPage.JSONToCSVConvertor($this.$chart_data_for_csv.val(), $this.$graph_type.val(), true);
     	});
     	
     	 this.$body.on("click",this.$graph_response.selector, function($e) {
 	    	var chart_id = $(this).attr('id');
 	    	$e.preventDefault();
 	    	$.ReportPage.get_response_graph(chart_id);
 	    
 	    });

        
     	 this.$body.on("click",this.$graph_attend_wise_pickup.selector, function($e) {
	    	var chart_id = $(this).attr('id');
	    	$e.preventDefault();
	    	$.ReportPage.get_attend_wise_pickup_graph(chart_id);
	    
	    });
     	
      	 this.$body.on("click",this.$graph_call_duration.selector, function($e) {
 	    	var chart_id = $(this).attr('id');
 	    	$e.preventDefault();
 	    	$.ReportPage.get_call_duration_graph(chart_id);
 	    
 	    });
	    
	    this.$body.on("click",this.$graph_pickup.selector, function($e) {
 	    	var chart_id = $(this).attr('id');
 	    	$e.preventDefault();
 	    	$.ReportPage.get_dial_vs_pickup_graph(chart_id);
 	    
 	    });
	    
	    this.$body.on("click",this.$graph_call_in.selector, function($e) {
 	    	var chart_id = $(this).attr('id');
 	    	$e.preventDefault();
 	    	$.ReportPage.get_call_in_graph(chart_id);
 	    
 	    });
	    
	    this.$body.on("click",this.$graph_forward.selector, function($e) {
	    	var chart_id = $(this).attr('id');
	    	$e.preventDefault();
	    	$.ReportPage.get_forward_graph(chart_id);
	    
	    });
	    
	    this.$body.on("click",this.$graph_total_minute_used.selector, function($e) {
	    	var chart_id = $(this).attr('id');	
	    	$e.preventDefault();
	    	$.ReportPage.get_total_minute_used_graph(chart_id);
	    
	    });
	   
	    this.$body.on("click",this.$graph_total_call_count.selector, function($e) {
	    	var chart_id = $(this).attr('id'); 	
	    	$e.preventDefault();
	    	$.ReportPage.get_total_call_count_graph(chart_id);
	    
	    });
	    
	    this.$body.on("click",this.$graph_credit_used.selector, function($e) {
	    	var chart_id = $(this).attr('id'); 	
	    	$e.preventDefault();
	    	$.ReportPage.get_credit_used_graph(chart_id);
	    
	    });
	    
	    this.$body.on("click",this.$graph_recharge.selector, function($e) {
	    	var chart_id = $(this).attr('id');
	    	$e.preventDefault();
	    	$.ReportPage.get_recharge_graph(chart_id);
	    
	    });
	    
	    this.$userselect.on('change',function($e) {
	
	    	$this.$select_group_div.show();
	    	$this.$select_broadcast_div.hide();
	    	$.ReportPage.select_user_event(this.value);
	    });
	    

	    this.$body.on("change",this.$groupselect.selector, function($e) {

	    	$this.$select_broadcast_div.show();
	    	$.ReportPage.select_group_event(this.value); 
	    });
	    
	    this.$body.on("change",this.$broadcastselect.selector, function($e) {
	
	       	$.ReportPage.select_broadcast_event(this.value); 
	    });
	    
	    this.$select_group_div.hide();
	    this.$select_broadcast_div.hide();
	    
    }, 
        
    $.ReportPage = new ReportPage, $.ReportPage.Constructor = ReportPage
    
}(window.jQuery),

function($) {
    "use strict";

    var UserSearch = function() {
        this.$body = $("body"),
        this.$searchString = $("#search_string"),
        this.$advanceSearchPanel = $("#advance_search_panel"),
        this.$userSearchForm = $("#usersearchform"),
        this.$advanceSearchLink = $("#advance_search_link"),
        this.$advanceSearchPanelAddFilterBtn = $("#advance_search_panel_addfilterbtn"),
        this.$addFilterBtn = $("#add_filter"),
        this.$submitBtn = $("#submit"),
        this.$saveExcel = $("#saveasexcel"),
        this.$errorContainer = $("#show-notification"),
        this.$saveFlagHiddenField = $("#saveFlag"),
        this.fileds,
        this.operators,
        this.types,
        this.counter = 0
    };    
    
    /*
    setData() set all data of fields, operator and typeData 
    */
    
    UserSearch.prototype.setData = function(fieldData, operatorData, typeData) {
    	this.fields = fieldData;
    	this.operators = operatorData;
    	this.types = typeData;
    }
    
    /*
    setDefaultData() is called with selected filter data and when post method call it redisplay all selected filters
    it call addField method one by one for all selected filters 
    */
    
    UserSearch.prototype.setDefaultData = function(selectedAndor,selectedField,selectedOperator,selectedeValue) {
    	
    	this.$advanceSearchPanelAddFilterBtn.show();
		this.$advanceSearchPanel.show();
    	
    	for (var i = 0; i < selectedAndor.length; i++) { 
    		$.UserSearch.addField(selectedAndor[i],selectedField[i],selectedOperator[i],selectedeValue[i]);
    	}	
    }
 
    /*
    setSearchString() sat universal search data and display back 
    */
    
    UserSearch.prototype.setSearchString = function(data) {
    	this.$searchString.val(data)
    }
    
    /*
    addField() is used to add new filter  
    */
    
    UserSearch.prototype.addField = function(selectedAndor,selectedfield,selectedoperator,selectedvalue) {
    	
    	
    	this.counter = this.counter + 1 ;
    	
    	/*
    	FilterContainer div is for contain whole filter  
    	*/
    	var filterContainer = document.createElement("div");
    	filterContainer.className = "row p-l-20 p-b-10 form-group-sm";
    	
    		/*
    		andorDiv is for div for contain select tag for AND/OR operator  
    		*/
    		var andorDiv = document.createElement("div");
    		andorDiv.className = "col-md-1 ";
    		andorDiv.setAttribute('id', 'andorDiv_'+this.counter)
    			
    			/*
    			Create Select Filed with AND/OR options
    			and add it to FilterContainer
    			*/
    		
    		 	var selectAndorTag = document.createElement("SELECT");
    		    selectAndorTag.setAttribute('id', 'andor_'+this.counter);
    		 	selectAndorTag.className = "andor form-control ";
    		
	    		 	var optionAnd = document.createElement("option");
	    		 	optionAnd.setAttribute("value", "AND");
	    		 	var optionAndText = document.createTextNode("AND");
	    		 	optionAnd.appendChild(optionAndText);
	    		 	if (selectedAndor != "OR")
	    		 	{
	    		 		optionAnd.setAttribute("selected", "selected");
	    		 	}
	    		 	selectAndorTag.appendChild(optionAnd);
	    		 	
	    		 	var optionOr = document.createElement("option");
	    		 	optionOr.setAttribute("value", "OR");
	    		 	var optionOrText = document.createTextNode("OR");
	    		 	optionOr.appendChild(optionOrText);
	    		 	if (selectedAndor == "OR")
	    		 	{
	    		 		
	    		 		optionOr.setAttribute("selected", "selected");
	    		 		
	    		 	}	    		 	
	    		 	selectAndorTag.appendChild(optionOr);
	    		 	
	    		 andorDiv.appendChild(selectAndorTag);
	    	filterContainer.appendChild(andorDiv);
	    	
	    	/*
    		fieldLabelDiv is for div for contain Field label  
    		*/
	    	
	    	var fieldLabelDiv = document.createElement("div");
	    	fieldLabelDiv.className = "col-md-1 ";
	    	fieldLabelDiv.setAttribute('id', 'fieldLabelDiv_'+this.counter)
	    	
		    	var fieldLabel = document.createElement("LABEL");
		    	fieldLabel.className = "control-label"
		    	var fieldLabelText = document.createTextNode("Field ");
		    	fieldLabel.appendChild(fieldLabelText);
		    	
		    	fieldLabelDiv.appendChild(fieldLabel);
		    filterContainer.appendChild(fieldLabelDiv);
	    	
	    	
		    /*
    		fieldSelectDiv is for div for contain Field select tag and add it to filterContainer  
    		*/
	    	var fieldSelectDiv = document.createElement("div");
	    	fieldSelectDiv.className = "col-md-2";
	    	fieldSelectDiv.setAttribute('id', 'fieldSelectDiv_'+this.counter)
	    		
	    		var selectFieldTag = document.createElement("SELECT");
	    		selectFieldTag.className = "fieldchange form-control";
	    		selectFieldTag.setAttribute('id', 'field_'+this.counter);
	    		/*
	    		loop through all fields one by one and create option for all and add it to select tag
	    		if field is selected then set that field as selected field 
	    		*/
	    		for(var i = 0; i <  this.fields.length ; i++)
	    		{
	    			
	    			var option = document.createElement("option");
	    		 	option.setAttribute("value", this.fields[i]);
	    		 	
	    		 	if (selectedfield == this.fields[i])
	    		 	{
	    		 		
	    		 		option.setAttribute("selected", "selected");
	    		 		
	    		 	}
	    		 	
	    		 	var optionText = document.createTextNode(this.fields[i]);
	    		 	option.appendChild(optionText);
	    		 	selectFieldTag.appendChild(option);
	    		 	
	    		}
	    		fieldSelectDiv.appendChild(selectFieldTag);
	    	filterContainer.appendChild(fieldSelectDiv);
	    	
	    	/*
    		operatorLabelDiv is for div for contain Operator label  
    		*/
	    	
	    	var operatorLabelDiv = document.createElement("div");
	    	operatorLabelDiv.className = "col-md-1";
	    	operatorLabelDiv.setAttribute('id', 'operatorLabelDiv_'+this.counter)
	    	
		    	var operatorLabel = document.createElement("LABEL");
		    	operatorLabel.className = "control-label"
		    	var operatorLabelText = document.createTextNode("Operator ");
		    	operatorLabel.appendChild(operatorLabelText);
		    	
		    	operatorLabelDiv.appendChild(operatorLabel);
	    	
		    filterContainer.appendChild(operatorLabelDiv);
	    	
		    /*
    		operatorSelectDiv is for div for contain operator select tag and add it to filterContainer  
    		*/
	    	
	    	var operatorSelectDiv = document.createElement("div");
	    	operatorSelectDiv.className = "col-md-2	";
	    	operatorSelectDiv.setAttribute('id', 'operatorSelectDiv_'+this.counter)
	    	
	    		var selectOperator = document.createElement("SELECT");
	    		selectOperator.className = "form-control operator";
	    		selectOperator.setAttribute('id', 'operator_'+this.counter);
	    		
	    		/*
	    		if any field is selected then we want to display that field's operator otherwise display 1st fields operator
	    		so if selected field then index = index of selected field otherwise it set to 0
	    		*/
	    		
	    		if(selectedfield) {
	    			var index = this.fields.indexOf(selectedfield);
	    		}
	    		else {
	    			var index = 0;
	    		}
	    		
	    		/*
	    		found operator string by index it return whole string of operators seprated by Comma(,)
	    		then split it and loop throught it and append it to operator options
	    		*/
	    		var stringOperator = this.operators[index];
	    		var operatorArray = stringOperator.split(',');	
	    	
	    		for(var i = 0; i <  operatorArray.length ; i++) {
	    			
	    			var option = document.createElement("option");
	    			var actualoperator = $("<div/>").html(operatorArray[i]).text()
	    		 	option.setAttribute("value", actualoperator);
	    		 	
	    		 	if (selectedoperator == operatorArray[i]) {
	    		 		
	    		 		option.setAttribute("selected", "selected");
	    		 		
	    		 	}
	    		 	
	    		 	var optionText = document.createTextNode(actualoperator);
	    		 	option.appendChild(optionText);
	    		 	selectOperator.appendChild(option);
	    		}
	    		operatorSelectDiv.appendChild(selectOperator);
	    	filterContainer.appendChild(operatorSelectDiv);
	    	
	    	/*
    		amountLabelDiv is for div for contain Amount label  
    		*/
	    	
	    	var amountLabelDiv = document.createElement("div");
	    	amountLabelDiv.className = "col-md-1";
	    	amountLabelDiv.setAttribute('id', 'amountLabelDiv_'+this.counter)
	    	
		    	var amountLabel = document.createElement("LABEL");
		    	amountLabel.className = "control-label"
		    	var amountLabelText = document.createTextNode("Value ");
		    	amountLabel.appendChild(amountLabelText);
		    	
		    	amountLabelDiv.appendChild(amountLabel);
	    	
	    	filterContainer.appendChild(amountLabelDiv);
	    	
	    	/*
    		amountTextDiv is for div for contain amount input box  
    		*/
	    	
	    	var amountTextDiv = document.createElement("div");
	    	amountTextDiv.className = "col-md-3";
	    	amountTextDiv.setAttribute('id', 'amountTextDiv_'+this.counter)
	    	
	    		var amountTextBox = document.createElement("input");
	    		amountTextBox.setAttribute('id', 'value_'+this.counter)
	    		
	    		amountTextBox.className = "values form-control";
	    		amountTextBox.setAttribute('type', 'text');
	    		amountTextBox.setAttribute('placeholder', 'Enter Search Word');
	    			
	    		/*
	    		if selected value then fill that value in inputbox  
	    		*/
	    		if (selectedvalue)
	    		{
	    			amountTextBox.setAttribute('value', selectedvalue);
    			}
	    		
	    		amountTextDiv.appendChild(amountTextBox);
	    	filterContainer.appendChild(amountTextDiv);

	    	/*
    		removeButtonDiv is for div for contain Remove Button  
    		*/
	    	
	    	var removeButtonDiv = document.createElement("div");
	    	removeButtonDiv.className = "col-md-1";
	    	removeButtonDiv.setAttribute('id', 'removeButtonDiv_'+this.counter)
	    		
	    	 	var removeButton = document.createElement('button');
	    	 	removeButton.className = "removeclass0 btn-danger p-t-5";
	    	 	var removeButtonText = document.createTextNode("X");
	    	 	removeButton.appendChild(removeButtonText);
	    	 	removeButtonDiv.appendChild(removeButton);
	    	 
	    	 filterContainer.appendChild(removeButtonDiv);
	    /*
	    Append whole filter container to advancesearchpanel for display it  
	    */
	    this.$advanceSearchPanel.append(filterContainer);
	    
	    /*
	    Set SelectPicker for all select Tag  
	    */
	    
	    $("#andor_"+this.counter).selectpicker();
	    $("#field_"+this.counter).selectpicker();
	    $("#operator_"+this.counter).selectpicker();
	    
	    /*
	    select picker add same class of select to next div so remove from next div  
	    */
	    
	    $("#andor_"+this.counter).next('div').removeClass('andor');
	    $("#field_"+this.counter).next('div').removeClass('fieldchange');
	    $("#operator_"+this.counter).next('div').removeClass('operator');
	    
	    /*
	    if selected value then check if it is date then set that inputbox to datepicker  
	    */
	    if (selectedvalue)
	    {
	    	var index = this.fields.indexOf(selectedfield);
			var type = this.types[index];
	    	if(type == 'date')
	    	{
	    		$("#value_"+this.counter).datepicker({'format': 'yyyy-mm-dd', 'autoclose': true, 'orientation': 'bottom'});
	    	}
	    }
    }
    
    /*
    if click on advance search link then addfilterbtn and searchpanel toggle
    means if it is visible then hide or vice versa  
    */
    
    UserSearch.prototype.advanceSearchLink = function() {
    	this.$advanceSearchPanelAddFilterBtn.toggle();
		this.$advanceSearchPanel.toggle();
    }
    
    /*
    When submit form then it get create hiddenform field for all filters 
    */
    UserSearch.prototype.submit = function() {
    	
    	// get value from all andor select tag 
    	
    	var andor = [];
		$.each($('.andor'), function() {
   			andor.push($(this).val());
   			
		});
		
		// get value from all field select tag 
		
		var fields = [];
	  	$.each($('.fieldchange'), function() {
   			fields.push($(this).val());
		});
		
	  	// get value from all andor operator tag 
	  	
	  	var operators = [];
	  	$.each($('.operator'), function() {
   			operators.push($(this).val());
		});
		
	  	// get value from all input box 
	  	
	  	var values = [];
	  	$.each($('.values'), function() {
   			values.push($(this).val());
		});

	  	/*
	  	loop througth all filters and create hidden field and append it to form  
	  	*/
    	for (var i = 0; i < fields.length; i++) 
		{
    		var data = andor[i] + ',' + fields[i] + ',' + operators[i] + ',' + values[i];
    		var hiddenfield = document.createElement("input");
    		hiddenfield.setAttribute("type", "hidden");
    		hiddenfield.setAttribute("name", "hiddenfield");
    		hiddenfield.setAttribute("value", data);
    		this.$userSearchForm.append(hiddenfield)
		} 	
    	
    	return true;
    }
    /*
    when field change then this function is called it takes 3 arguments
    thisid = changed field select tag id
    changedataid = operator select tag id in which we feel operartor as selected field
    changetextfieldid = inputbox id which is in this filter for set datepicker or not  
    */
    
    UserSearch.prototype.changeOperator = function(thisId,changeDataId,changeTextFieldId) {
    	
    	/*
    	select comma(,) seprated operator string connected to selected field 
    	*/
    	var getValue = $(thisId).val();
    	var index = this.fields.indexOf(getValue);
    	var stringOperator = this.operators[index];
    	var operatorArray = stringOperator.split(',');
    	var string = "";
    	for(var i = 0; i < operatorArray.length  ; i++) 
    	{
    		string = string + '<option> ';
    		string = string + operatorArray[i];
    		string = string + '</option> ';
    	}
    	
    	/*
    	in operator select tag remove old options and add new options  
    	*/
    	
    	$(changeDataId).empty().append(string);
    	$(changeDataId).selectpicker('refresh');
    	$(changeDataId).next('div').removeClass('operator');
    	var type = this.types[index];
    	
    	/*
    	remove old textbox and add new textbox
    	if type of data is date then add datepicker to it 
    	*/
    	
    	var textBox = document.createElement("input");
		textBox.className = "values form-control"
		textBox.setAttribute('id', changeTextFieldId)
		var id = $("#" + changeTextFieldId).parent('div').attr('id');
		$("#" + changeTextFieldId).remove();
		
		
    	if (type == 'date')
    	{
    		textBox.setAttribute('placeholder', 'Select Date');	
    		$("#"+id).append(textBox);
    		$("#" + changeTextFieldId).datepicker({'format': 'yyyy-mm-dd', 'autoclose': true, 'orientation': 'bottom'});
    	}
    	else
    	{
    		textBox.setAttribute('type', 'text');
    		textBox.setAttribute('placeholder', 'Enter Search Word');
    		$("#"+id).append(textBox);
    	}	
    }
    
    UserSearch.prototype.init = function() {
    
    	var $this = this;

    	this.$saveExcel.click(function() {
    		document.getElementById("saveFlag").value = true;
    		//this.$saveFlagHiddenField.setValue(true);
    		
    	
    	});
    	
    	this.$submitBtn.click(function() {
    		document.getElementById("saveFlag").value = false;
    		//this.$saveFlagHiddenField.setValue(true);
    	});
    	
    	
        this.$userSearchForm.submit(function(event)  {
        	
        	$.UserSearch.submit();
        });
    	
    	this.$advanceSearchLink.click(function() {
    		$.UserSearch.advanceSearchLink();
    		
    		return false;
    	});
    	
    	this.$addFilterBtn.click(function() {
    		
    		$.UserSearch.addField();
    	});
    	

    	
		this.$body.on("click", ".removeclass0", function() {
			
			//when click remove button then remove whole filter
			
			$(this).closest("div").parent("div").remove();
		});
		
		this.$body.on("click", ".accountdetail", function() {
			
			/*
			when select account detail of user then add account detail to localstorage 
			so when it forward to setting page then account detail tab is selected
			*/
			
			var id = "user-action-tab"
			var key = 'lastTag';
			key += ':' + id; 
			localStorage.setItem(key, "#account-dt");	
		});
		
		this.$body.on("click", ".streamaccount", function() {
			
			/*
			when select stream acoount of user then add stream account to localstorage 
			so when it forward to setting page then account setting tab is selected
			*/
			
			var id = "user-action-tab"
			var key = 'lastTag';
			key += ':' + id;
			localStorage.setItem(key, "#streamacc");
		});
		
		this.$body.on("click", ".recharge", function() {
			
			/*
			when select recharge of user then add recharge to localstorage 
			so when it forward to setting page then recharge tab is selected
			*/
			
			var id = "user-action-tab"
			var key = 'lastTag';
			key += ':' + id;
			 
			localStorage.setItem(key, "#recharge");
		});

		this.$body.on("change", ".fieldchange", function() {
			
			/*
			when user change filed then operator is changed and input box is changes 
			so it call changeoperator function with 3 arguments
			1 = change field id
			2 = operator id that need to be change
			3 = textbox id that need to be change 
			*/
			
			var thisId = '#' + $(this).attr('id');
			var changeDataId = '#' + $(this).closest("div").next("div").next("div").children().attr('id');
			var changeTextFieldId = $(this).closest("div").next("div").next("div").next("div").next("div").children().attr('id');
			$.UserSearch.changeOperator(thisId,changeDataId,changeTextFieldId);
		});
		
		if(this.$errorContainer.length > 0) {
			
			/*
			if error accour then displat that error 
			*/
			
    		var type = this.$errorContainer.attr('data-type');
    		var msg = this.$errorContainer.attr('data-message'); 
    		
    		
    	}
		
    },
    $.UserSearch = new UserSearch, $.UserSearch.Constructor = UserSearch
    
}(window.jQuery),

//portlets
function($) {
    "use strict";

    /**
    Portlet Widget
    */
    var Portlet = function() {
        this.$body = $("body"),
        this.$portletIdentifier = ".portlet",
        this.$portletCloser = '.portlet a[data-toggle="remove"]',
        this.$portletRefresher = '.portlet a[data-toggle="reload"]'
    };

    //on init
    Portlet.prototype.init = function() {
        // Panel closest
        var $this = this;
        $(document).on("click",this.$portletCloser, function (ev) {
            ev.preventDefault();
            var $portlet = $(this).closest($this.$portletIdentifier);
                var $portlet_parent = $portlet.parent();
            $portlet.remove();
            if ($portlet_parent.children().length == 0) {
                $portlet_parent.remove();
            }
        });

        // Panel Reload
        $(document).on("click",this.$portletRefresher, function (ev) {
            ev.preventDefault();
            var $portlet = $(this).closest($this.$portletIdentifier);
            // This is just a simulation, nothing is going to be reloaded
            $portlet.append('<div class="panel-disabled"><div class="loader-1"></div></div>');
            var $pd = $portlet.find('.panel-disabled');
            setTimeout(function () {
                $pd.fadeOut('fast', function () {
                    $pd.remove();
                });
            }, 500 + 300 * (Math.random() * 5));
        });
    },
    //
    $.Portlet = new Portlet, $.Portlet.Constructor = Portlet
    
}(window.jQuery),
 
function($) {
    "use strict";

    var RickshawChart = function() {
        this.$body = $("body")
    };
    //creates area graph
    RickshawChart.prototype.createAreaGraph = function(selector, seriesData, random, colors, labels, data_length) {
      
      var areaGraph = new Rickshaw.Graph( {
          element: document.querySelector(selector),
          renderer: 'area',
          stroke: true,
          height: 250,
          preserve: true,
          series: [
            {
              color: colors[0],
              data: seriesData[0],
              name: labels[0]
            }, 
            {
              color: colors[1],
              data: seriesData[1],
              name: labels[1]
            }
          ]
      });
   
      var hoverDetail = new Rickshaw.Graph.HoverDetail( {
          graph: areaGraph
        } );

      
      areaGraph.render();
      
      
      setInterval( function() {
   
    	  $.ajax({
  			url: $.DashboardPage.graph_url_data["live_call_last_15sec_data"],
  			method: "POST",
  			data : 
			{'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(), chart_type : "live_call_chart"
			},
  			complete: function (response) 
  			{
  				var group_data = jQuery.parseJSON(response.responseText);
  				
  				seriesData[0].shift();
  				seriesData[1].shift();
  				seriesData[0].push({"x": data_length, "y": group_data["realtime_call_data"]["pickup"]});
  				seriesData[1].push({"x": data_length, "y": group_data["realtime_call_data"]["dial"]});
  				data_length = data_length + 1;
  			},dataType: 'json',	
  		});
    	 
    	  areaGraph.update();
      }, 20000 );
      
      $(window).resize(function(){
          areaGraph.render();
      });

    },
    
    RickshawChart.prototype.createSimpleareaGraph = function(selector, simpleAdata,colors) {
        var Simplearea = new Rickshaw.Graph( {
            element: document.querySelector(selector),
            renderer: 'area',
            stroke: true,
            series: [ {
                    data: simpleAdata,
                    color: colors[0]
            },]  
        });
        Simplearea.render();
    },
    RickshawChart.prototype.createMultipleareaGraph = function(selector, multipleAdata1,multipleAdata2,colors) {
        var Multiplearea = new Rickshaw.Graph( {
            element: document.querySelector(selector),
            renderer: 'area',
            stroke: true,
            series: [ {
                data: multipleAdata1,
                color: colors[0],
                border: 0
        }, {    
                data: multipleAdata2,
                color: colors[1]
        }]    
        });
        Multiplearea.render();
    },
    RickshawChart.prototype.createLinetoggleGraph = function(selector, height, colors, names) {
      // set up our data series with 50 random data points

      var seriesData = [ [], [], [] ];
      var random = new Rickshaw.Fixtures.RandomData(150);

      for (var i = 0; i < 150; i++) {
        random.addData(seriesData);
      }

      // instantiate our graph!

      var graph = new Rickshaw.Graph( {
        element: document.getElementById(selector),
        height: height,
        renderer: 'line',
        series: [
          {
            color: colors[0],
            data: seriesData[0],
            name: names[0]
          }, {
            color: colors[1],
            data: seriesData[1],
            name: names[1]
          }, {
            color: colors[2],
            data: seriesData[2],
            name: names[2]
          }
        ]
      } );

      
      graph.render();

      var hoverDetail = new Rickshaw.Graph.HoverDetail( {
        graph: graph,
        formatter: function(series, x, y) {
          var date = '<span class="date">' + new Date(x * 1000).toUTCString() + '</span>';
          var swatch = '<span class="detail_swatch" style="background-color: #000' + series.color + '"></span>';
          var content = swatch + series.name + ":" + parseInt(y) + date;
          return content;
        }
      } );
    },
    RickshawChart.prototype.createLinePlotGraph = function(selector, colors, names ,data) {
      var graph = new Rickshaw.Graph( {
        element: document.getElementById(selector),
        renderer: 'lineplot',
        padding: { top: 0.1 },
        series: [
          {
            data: data[0],
            color: colors[0],
            name: names[0]
          }, {
            data: data[1],
            color: colors[1],
            name: names[1]
          }
        ]
      } );

      var hover = new Rickshaw.Graph.HoverDetail({ graph: graph,
          formatter: function(series, x, y) {
        	 
              var swatch = '<span class="detail_swatch" style="background-color: #000' + series.color + '"></span>';
              var content = swatch + series.name + " : " + parseInt(y);
              return content;
            }
          } );


      graph.render();
    },
    RickshawChart.prototype.createMultiGraph = function(selector, height, names, colors) {
      var seriesData = [ [], [], [], [], [] ];
      var random = new Rickshaw.Fixtures.RandomData(50);

      for (var i = 0; i < 75; i++) {
        random.addData(seriesData);
      }

      var graph = new Rickshaw.Graph( {
        element: document.getElementById(selector),
        renderer: 'multi',
        height: height,
        dotSize: 5,
        series: [
          {
            name: names[0],
            data: seriesData.shift(),
            color: colors[0],
            renderer: 'stack'
          }, {
            name: names[1],
            data: seriesData.shift(),
            color: colors[1],
            renderer: 'stack'
          }, {
            name: names[2],
            data: seriesData.shift(),
            color: colors[2],
            renderer: 'scatterplot'
          }, {
            name: names[3],
            data: seriesData.shift().map(function(d) { return { x: d.x, y: d.y / 4 } }),
            color: colors[3],
            renderer: 'bar'
          }, {
            name: names[4],
            data: seriesData.shift().map(function(d) { return { x: d.x, y: d.y * 1.5 } }),
            color: colors[4],
            renderer: 'line'
            
          }
        ]
      } );

      graph.render();

      var detail = new Rickshaw.Graph.HoverDetail({
        graph: graph
      });

      var legend = new Rickshaw.Graph.Legend({
        graph: graph,
        element: document.querySelector('#legend')
      });

      var highlighter = new Rickshaw.Graph.Behavior.Series.Highlight({
          graph: graph,
          legend: legend,
          disabledColor: function() { return '#ddd' }
      });

      var highlighter = new Rickshaw.Graph.Behavior.Series.Toggle({
          graph: graph,
          legend: legend
      });
    },
    RickshawChart.prototype.stringToDate = function(_date,_format,_delimiter)
    {
                var formatLowerCase=_format.toLowerCase();
                var formatItems=formatLowerCase.split(_delimiter);
                var dateItems=_date.split(_delimiter);
                var monthIndex=formatItems.indexOf("mm");
                var dayIndex=formatItems.indexOf("dd");
                var yearIndex=formatItems.indexOf("yyyy");
                var month=parseInt(dateItems[monthIndex]);
                month-=1;
                var formatedDate = new Date(dateItems[yearIndex],month,dateItems[dayIndex]);
                return formatedDate;
    },
    //initializing various charts and components
    RickshawChart.prototype.createLiveCallGraph = function(live_call_data)
    {
    	var seriesData = [ [], [], [], [], [], [], [], [], [] ];
        var random = new Rickshaw.Fixtures.RandomData(1);
        var data_length = 100;
        for (var i = 0; i < data_length; i++) {
          seriesData[0].push({"x":i, "y": live_call_data["pickup"][i]})
      	  seriesData[1].push({"x":i, "y": live_call_data["dial"][i]})
        }
        
        //create live area graph
        var colors = ['#ff962f', '#E9E9E9'];
        var labels = ['Pickup','Attempts'];
        this.createAreaGraph("#linechart", seriesData, random, colors, labels,data_length);
        
    }
    
    RickshawChart.prototype.init = function(call_vs_pickup_graph_data) {
      
    },
	
    //init dashboard
    $.RickshawChart = new RickshawChart, $.RickshawChart.Constructor = RickshawChart
    
}(window.jQuery),


function($) {
    "use strict";

    var Sparkline = function() {
    	var month_data = [];
    };

    //
    Sparkline.prototype.create_portlet_signup_user_per_month = function(graph_data) {
    	var $this= this;
    	
    	$('.inlinesparkline').sparkline(graph_data["signup_data"], {
            type: 'line',
            width: '100%',
            height: '32',
            lineWidth: 2,
            lineColor: 'rgba(26,41,66,0.7)',
            fillColor: 'rgba(59,192,195,0.5)',
            highlightSpotColor: '#3bc0c3',
            highlightLineColor: '#1a2942',
            spotRadius: 3,
            tooltipFormat : '<span style="font-size: 18px"> Signups : {{y}} <br> {{x:month}} - {{x:year}} '  +'</span>',
            tooltipValueLookups: {
                "month": {
                    0: $this.month_data[( (parseInt(graph_data["start_month"] -1 ) % 12) )],
                    1: $this.month_data[( ( parseInt(graph_data["start_month"]) + 0 ) % 12)],
                    2: $this.month_data[( ( parseInt(graph_data["start_month"]) + 1 ) % 12)],
                    3: $this.month_data[( ( parseInt(graph_data["start_month"]) + 2 ) % 12)],
                    4: $this.month_data[( ( parseInt(graph_data["start_month"]) + 3 ) % 12)],
                    5: $this.month_data[( ( parseInt(graph_data["start_month"]) + 4 ) % 12)],
                    6: $this.month_data[( ( parseInt(graph_data["start_month"]) + 5 ) % 12)],
                    7: $this.month_data[( ( parseInt(graph_data["start_month"]) + 6 ) % 12)],
                    8: $this.month_data[( ( parseInt(graph_data["start_month"]) + 7 ) % 12)],
                    9: $this.month_data[( ( parseInt(graph_data["start_month"]) + 8 ) % 12)],
                    10:$this.month_data[( ( parseInt(graph_data["start_month"]) + 9 ) % 12)],
                    11:$this.month_data[( ( parseInt(graph_data["start_month"]) + 10 ) % 12)],
                    // Add more here
                	},
    			"year": {
    				0:  parseInt(graph_data["start_year"]) + parseInt(parseInt(graph_data["start_month"]-1) / 12 ),
                    1: parseInt(graph_data["start_year"]) + parseInt(parseInt(graph_data["start_month"]+0) / 12 ) ,
                    2: parseInt(graph_data["start_year"]) + parseInt(parseInt(graph_data["start_month"]+1) / 12 ) ,
                    3: parseInt(graph_data["start_year"]) + parseInt(parseInt(graph_data["start_month"]+2) / 12 ) ,
                    4: parseInt(graph_data["start_year"]) + parseInt(parseInt(graph_data["start_month"]+3) / 12 ) ,
                    5: parseInt(graph_data["start_year"]) + parseInt(parseInt(graph_data["start_month"]+4) / 12 ) ,
                    6: parseInt(graph_data["start_year"]) + parseInt(parseInt(graph_data["start_month"]+5) / 12 ) ,
                    7: parseInt(graph_data["start_year"]) + parseInt(parseInt(graph_data["start_month"]+6) / 12 ) ,
                    8: parseInt(graph_data["start_year"]) + parseInt(parseInt(graph_data["start_month"]+7) / 12 ) ,
                    9: parseInt(graph_data["start_year"]) + parseInt(parseInt(graph_data["start_month"]+8) / 12 ) ,
                    10: parseInt(graph_data["start_year"]) + parseInt(parseInt(graph_data["start_month"]+9) / 12 ) ,
                    11: parseInt(graph_data["start_year"]) + parseInt(parseInt(graph_data["start_month"]+10) / 12 ) ,
                    
    			}
            }
        });
    },
    
    Sparkline.prototype.create_portlet_recharge_per_month = function(graph_data) {
    	var $this = this;
    	$('.dynamicbar-big').sparkline(graph_data["recharge_data"], {
            type: 'bar',
            barColor: '#3bc0c3',
            height: '32',
            barWidth: 24,
            barSpacing: 5,
            tooltipFormat : '<span style="font-size: 18px"> Recharge : {{value}} </span>',
        });
    },
    
    Sparkline.prototype.create_call_in_by_hour = function(graph_data,div_id) {
    	var $this = this;
    	$(div_id).show();
    	
    	var array_data = [];
    	for (var i = 0; i<24;i++)
    	{
    		if(graph_data["data"].hasOwnProperty(i)){
    			array_data.push(parseInt(graph_data["data"][i]))
    		}
    		else
    		{
    			array_data.push(parseInt(0));
    		}
    		
    	}
    	$('.call-in-chart').sparkline(array_data, {
    		type: 'line',
            width: '100%',
            height: '100%',
            lineWidth: 3,
            drawNormalOnTop : true,
            drawXAxis: show_box,
            drawYAxis: show_box,
            drawXGrid: show_box,
            drawYGrid: show_box,
            lineColor: 'rgba(26,41,66,0.7)',
            fillColor: 'rgba(59,192,195,0.5)',
            highlightSpotColor: '#3bc0c3',
            highlightLineColor: '#1a2942',
            spotRadius: 3,
            tooltipFormat : '<span style="font-size: 18px"> Hour : {{x}} <br>' + graph_data["key"]+ ': {{y}} </span>',
        });
    },
    
    Sparkline.prototype.create_portlet_credit_used_per_month = function(graph_data) {
    	var $this = this;
    	$('#compositeline').sparkline(graph_data["credit_data"], {
            fillColor: false,
            changeRangeMin: 0,
            chartRangeMax: 10,
            type: 'line',
            width: '100%',
            height: '32',
            lineWidth: 2,
            lineColor: '#1a2942',
            highlightSpotColor: '#3bc0c3',
            highlightLineColor: '#f13c6e',
            spotRadius: 4,
            tooltipFormat : '<span style="font-size: 18px"> Credit Purchase : {{y}} <br> {{x:month}} - {{x:year}} '  +'</span>',
            tooltipValueLookups: {
                "month": {
                    0: $this.month_data[( (parseInt(graph_data["start_month"] -1 ) % 12) )],
                    1: $this.month_data[( ( parseInt(graph_data["start_month"]) + 0 ) % 12)],
                    2: $this.month_data[( ( parseInt(graph_data["start_month"]) + 1 ) % 12)],
                    3: $this.month_data[( ( parseInt(graph_data["start_month"]) + 2 ) % 12)],
                    4: $this.month_data[( ( parseInt(graph_data["start_month"]) + 3 ) % 12)],
                    5: $this.month_data[( ( parseInt(graph_data["start_month"]) + 4 ) % 12)],
                    6: $this.month_data[( ( parseInt(graph_data["start_month"]) + 5 ) % 12)],
                    7: $this.month_data[( ( parseInt(graph_data["start_month"]) + 6 ) % 12)],
                    8: $this.month_data[( ( parseInt(graph_data["start_month"]) + 7 ) % 12)],
                    9: $this.month_data[( ( parseInt(graph_data["start_month"]) + 8 ) % 12)],
                    10:$this.month_data[( ( parseInt(graph_data["start_month"]) + 9 ) % 12)],
                    11:$this.month_data[( ( parseInt(graph_data["start_month"]) + 10 ) % 12)],
                    // Add more here
                	},
    			"year": {
    				0:  parseInt(graph_data["start_year"]) + parseInt(parseInt(graph_data["start_month"]-1) / 12 ),
                    1: parseInt(graph_data["start_year"]) + parseInt(parseInt(graph_data["start_month"]+0) / 12 ) ,
                    2: parseInt(graph_data["start_year"]) + parseInt(parseInt(graph_data["start_month"]+1) / 12 ) ,
                    3: parseInt(graph_data["start_year"]) + parseInt(parseInt(graph_data["start_month"]+2) / 12 ) ,
                    4: parseInt(graph_data["start_year"]) + parseInt(parseInt(graph_data["start_month"]+3) / 12 ) ,
                    5: parseInt(graph_data["start_year"]) + parseInt(parseInt(graph_data["start_month"]+4) / 12 ) ,
                    6: parseInt(graph_data["start_year"]) + parseInt(parseInt(graph_data["start_month"]+5) / 12 ) ,
                    7: parseInt(graph_data["start_year"]) + parseInt(parseInt(graph_data["start_month"]+6) / 12 ) ,
                    8: parseInt(graph_data["start_year"]) + parseInt(parseInt(graph_data["start_month"]+7) / 12 ) ,
                    9: parseInt(graph_data["start_year"]) + parseInt(parseInt(graph_data["start_month"]+8) / 12 ) ,
                    10: parseInt(graph_data["start_year"]) + parseInt(parseInt(graph_data["start_month"]+9) / 12 ) ,
                    11: parseInt(graph_data["start_year"]) + parseInt(parseInt(graph_data["start_month"]+10) / 12 ) ,
                    
    			}
            }
        });
    },
    
    Sparkline.prototype.create_portlet_minute_used_per_month = function(graph_data) {
    	$('.sparkpie-big').sparkline(graph_data["minute_used_data"], {
            type: 'pie',
            width: '100%',
            height: '70',
            sliceColors: ['#EF5350', '#EC407A', '#AB47BC', '#7E57C2', '#5C6BC0', '#42A5F5', '#29B6F6', '#26C6DA', '#26A69A', '#66BB6A', '#9CCC65', '#D4E157'],
            offset: 0,
            borderWidth: 0,
            borderColor: '#00007f',
            tooltipFormat : '<span style="font-size: 18px; color:{{color}};" > Minute Used : {{value}} <br> Peratenge : {{percent}}% </span>',
        });
    },
    
    Sparkline.prototype.init = function() {
    	
    	this.month_data = [
    	"January",
		"February",
		"march",
		"April",
		"May",
		"June",
		"July",
		"August",
		"Suptember",
		"October",
		"Nevember",
		"December" ];
    },
    //init
    $.Sparkline = new Sparkline, $.Sparkline.Constructor = Sparkline
}(window.jQuery),
    
function($) {
        "use strict";
    	
        var DashboardPage = function() {
        	this.graph_url_data;
        };
        DashboardPage.prototype.set_graph_urls = function(data)
        {
        	this.graph_url_data = data;
        	$.DashboardPage.get_live_call_graph();
    		$.DashboardPage.get_portlet_signup_user();
    		$.DashboardPage.get_portlet_recharge();
    		$.DashboardPage.get_portlet_credit_used();
    		$.DashboardPage.get_portlet_minute_used();
    		
        }
        
        DashboardPage.prototype.get_portlet_minute_used = function()
        {
            var $this = this;
        	$.ajax({
    				url: $this.graph_url_data["home_portal_minute_used_per_month"],
    				method: "POST",
    				data : 
    				{'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(), chart_type : "portlet"
    				},
    				complete: function (response) 
    				{
    					var graph_data = jQuery.parseJSON(response.responseText);
    					
    					$.Sparkline.create_portlet_minute_used_per_month(graph_data);
    				},dataType: 'json',	
    			});
    	},
        
        
        
        DashboardPage.prototype.get_portlet_credit_used = function()
        {
            var $this = this;
        	$.ajax({
    				url: $this.graph_url_data["home_portal_credit_used_per_month"],
    				method: "POST",
    				data : 
    				{'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(), chart_type : "portlet"
    				},
    				complete: function (response) 
    				{
    					var graph_data = jQuery.parseJSON(response.responseText);
    					
    					$.Sparkline.create_portlet_credit_used_per_month(graph_data);
    				},dataType: 'json',	
    			});
    	},
        
        
        DashboardPage.prototype.get_portlet_recharge = function()
        {
            var $this = this;
        	$.ajax({
    				url: $this.graph_url_data["home_portal_recharge_per_month"],
    				method: "POST",
    				data : 
    				{'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(), chart_type : "portlet"
    				},
    				complete: function (response) 
    				{
    					var graph_data = jQuery.parseJSON(response.responseText);
    					
    					$.Sparkline.create_portlet_recharge_per_month(graph_data);
    				},dataType: 'json',	
    			});
    	},
        
        DashboardPage.prototype.get_portlet_signup_user = function()
        {
            var $this = this;
        	$.ajax({
    				url: $this.graph_url_data["home_portal_signup_per_month"],
    				method: "POST",
    				data : 
    				{'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(), chart_type : "portlet"
    				},
    				complete: function (response) 
    				{
    					var graph_data = jQuery.parseJSON(response.responseText);
    					
    					$.Sparkline.create_portlet_signup_user_per_month(graph_data);
    				},dataType: 'json',	
    			});
    	},
    	
    	DashboardPage.prototype.get_live_call_graph = function()
        {
            var $this = this;
        	$.ajax({
    				url: $this.graph_url_data["live_call_past_data"],
    				method: "POST",
    				data : 
    				{'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(), chart_type : "portlet"
    				},
    				complete: function (response) 
    				{
    					var graph_data = jQuery.parseJSON(response.responseText);
    					
    					$.RickshawChart.createLiveCallGraph(graph_data["realtime_call_data"]);	
    				},dataType: 'json',	
    			});
    	},
    	
    	       
        DashboardPage.prototype.init = function() {
    		$.Sparkline.init();
        }, 
        
        $.DashboardPage = new DashboardPage, $.DashboardPage.Constructor = DashboardPage
        
 }(window.jQuery),
    
    

//main app module
function($) {
    "use strict";
    
    var DashboardApp = function() {
        this.VERSION = "1.0.0", 
        this.AUTHOR = "Nikhil N", 
        this.SUPPORT = "info@awaaz.de", 
        this.pageScrollElement = "html, body", 
        this.$body = $("body"),
        this.$dashboardPage = $("#dashboard-container"),
        this.$userSettingPage = $("#usersetting-container"),
        this.$userSearchPage = $("#usersearch-container"),
        this.$reportPage = $("#report-container"),
        this.$addCouponPage = $("#add-coupon-container")
    };

    //initializing tooltip
    DashboardApp.prototype.initTooltipPlugin = function() {
        $.fn.tooltip && $('[data-toggle="tooltip"]').tooltip()
    }, 
    
    DashboardApp.prototype.initSelect2Plugin = function() {
        $.fn.select2 && $('[data-init-plugin="select2"]').each(function() {
            $(this).select2({
                
            }).on("select2-opening", function() {
                $.fn.scrollbar && $(".select2-results").scrollbar({
                    ignoreMobile: !1
                })
            })
        })
    },
    DashboardApp.prototype.initDateTimePicker = function() {
    	$('.datepickeryyyy-mm-dd').datepicker({'format': 'yyyy-mm-dd', 'autoclose': true, 'orientation': 'bottom'});
    	$('.datepicker').datepicker({'format': 'yyyy/M/d', 'autoclose': true, 'orientation': 'bottom'});
    	$('.datepicker').datepicker({'format': 'yyyy-mm-dd', 'autoclose': true, 'orientation': 'bottom'});
    	$('.datepicker').datepicker('update', new Date());
    	$('.timepicker').timepicker({'step': 5,'showDuration': false, 'scrollDefault': 'now', 'forceRoundTime': true, 'timeFormat': 'h:i A', 'minTime': '8:00am','maxTime': '10:00pm',});
    	$('.timepicker').timepicker('setTime', new Date());
    	$('.datepicker-range').datepicker({'format': 'yyyy/M/d', 'autoclose': true});
    },
    DashboardApp.prototype.initDataTable = function() {
    	var $table = $('.data-table');
    	var pageLen = (typeof($table.attr("data-pagesize")) != 'undefined')? parseInt($table.attr("data-pagesize")): 5; 
    	$table.dataTable({"paging": $table.attr("data-paging") == "true" ? true : false, "ordering": $table.attr("data-ordering") == "true" ? true : false,
    			"searching": $table.attr("data-searchable") == "true" ? true : false, "pageLength": pageLen,
    			"lengthChange": $table.attr("data-lengthchange") == "true" ? true : false,
    			"serverSide": $table.attr("data-serverside") == "true" ? true : false,
    	});
    },
    
    DashboardApp.prototype.initSwitcheryPlugin = function() {
        window.Switchery && $('[data-init-plugin="switchery"]').each(function() {
        	var scolor = $(this).attr('data-color');
        	var sec_color = $(this).attr('data-secondary');
        	var size = $(this).attr('data-size');
            new Switchery($(this).get(0), {
                color: scolor,
                secondaryColor:sec_color,
                size: size
            })
        })
    },
    
    DashboardApp.prototype.initFormGroupDefault = function() {
        $(".form-group.form-group-default").click(function() {
            $(this).find(":input").focus()
        }), $("body").on("focus", ".form-group.form-group-default :input", function() {
            $(".form-group.form-group-default").removeClass("focused"), $(this).parents(".form-group").addClass("focused")
        }), $("body").on("blur", ".form-group.form-group-default :input", function() {
            $(this).parents(".form-group").removeClass("focused"), $(this).val() ? $(this).closest(".form-group").find("label").addClass("fade") : $(this).closest(".form-group").find("label").removeClass("fade")
        }), $(".form-group.form-group-default .checkbox, .form-group.form-group-default .radio").hover(function() {
            $(this).parents(".form-group").addClass("focused")
        }, function() {
            $(this).parents(".form-group").removeClass("focused")
        })
    },
	
    //initializing popover
    DashboardApp.prototype.initPopoverPlugin = function() {
        $.fn.popover && $('[data-toggle="popover"]').popover()
    }, 

    //initializing nicescroll
    DashboardApp.prototype.initNiceScrollPlugin = function() {
        //You can change the color of scroll bar here
        $.fn.niceScroll &&  $(".nicescroll").niceScroll({ cursorcolor: '#9d9ea5', cursorborderradius: '0px'});
    },
    
    //initilizing 
    DashboardApp.prototype.init = function() {
        this.initTooltipPlugin(),
        this.initPopoverPlugin(),
        this.initNiceScrollPlugin(),
        this.initSelect2Plugin(),
    	this.initDateTimePicker(),
    	this.initSwitcheryPlugin(),
    	this.initFormGroupDefault(),
    	this.initDataTable();
        //creating side bar
    	$.SideBar.init();
        //if(this.$dashboardPage.length > 0)
    	//	$.DashboardPage.init();
    	//if(this.$userSearchPage.length > 0)
    	//	$.UserSearch.init();
    	if(this.$userSettingPage.length > 0)
    		$.UserSettingPage.init();
    	if(this.$addCouponPage.length > 0)
    		$.AddCouponPage.init();
    	//if(this.$reportPage.length > 0)
    	//	$.ReportPage.init();
    },

    $.DashboardApp = new DashboardApp, $.DashboardApp.Constructor = DashboardApp

}(window.jQuery),

//initializing main application module
function($) {
    "use strict";
    $.DashboardApp.init()
}(window.jQuery);

(function () {
    'use strict';
    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        var id = $(this).parents('[role="tablist"]').attr('id');
        var key = 'lastTag';
        if (id) {
            key += ':' + id;
        }
 
        localStorage.setItem(key, $(e.target).attr('href'));
    });
 
    $('[role="tablist"]').each(function (idx, elem) {
        var id = $(elem).attr('id');
        var key = 'lastTag';
        if (id) {
            key += ':' + id;
        }
 
        var lastTab = localStorage.getItem(key);
        if (lastTab) {
            $('[href="' + lastTab + '"]').tab('show');
        }
        
    });
})();

/* ==============================================
7.WOW plugin triggers animate.css on scroll
=============================================== */
var wow = new WOW(
    {
        boxClass: 'wow', // animated element css class (default is wow)
        animateClass: 'animated', // animation css class (default is animated)
        offset: 50, // distance to the element when triggering the animation (default is 0)
        mobile: false        // trigger animations on mobile devices (true is default)
    }
);
wow.init();
