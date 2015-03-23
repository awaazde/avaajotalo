/**
 *	Dashboard : Main JavaScript File
 *
 **/


! function($) {
    "use strict";
    var Notification = function(container, options) {
        function SimpleNotification() {
            if (self.notification.addClass("notif-simple"), self.alert.append(self.options.message), self.options.showClose) {
                var close = $('<button type="button" class="close" data-dismiss="alert"></button>').append('<span aria-hidden="true">&times;</span>').append('<span class="sr-only">Close</span>');
                self.alert.prepend(close)
            }
        }

        function BarNotification() {
            if (self.notification.addClass("notif-bar"), self.alert.append("<span>" + self.options.message + "</span>"), self.alert.addClass("alert-" + self.options.type), self.options.showClose) {
                var close = $('<button type="button" class="close" data-dismiss="alert"></button>').append('<span aria-hidden="true">&times;</span>').append('<span class="sr-only">Close</span>');
                self.alert.prepend(close)
            }
        }

        function CircleNotification() {
            self.notification.addClass("notif-circle");
            var table = "<div>";
            self.options.thumbnail && (table += '<div class="pgn-thumbnail"><div>' + self.options.thumbnail + "</div></div>"), table += '<div class="notif-message"><div>', self.options.title && (table += '<p class="bold">' + self.options.title + "</p>"), table += "<p>" + self.options.message + "</p></div></div>", table += "</div>", self.options.showClose && (table += '<button type="button" class="close" data-dismiss="alert">', table += '<span aria-hidden="true">&times;</span><span class="sr-only">Close</span>', table += "</button>"), self.alert.append(table), self.alert.after('<div class="clearfix"></div>')
        }

        function FlipNotification() {
            if (self.notification.addClass("notif-flip"), self.alert.append("<span>" + self.options.message + "</span>"), self.options.showClose) {
                var close = $('<button type="button" class="close" data-dismiss="alert"></button>').append('<span aria-hidden="true">&times;</span>').append('<span class="sr-only">Close</span>');
                self.alert.prepend(close)
            }
        }
        var self = this;
        return self.container = $(container), self.notification = $('<div class="notif"></div>'), 
        	self.options = $.extend(!0, {}, $.fn.appNotification.defaults, options), 
        	self.container.find(".notif-wrapper[data-position=" + this.options.position + "]").length ? self.wrapper = $(".notif-wrapper[data-position=" + this.options.position + "]") : (self.wrapper = $('<div class="notif-wrapper" data-position="' + this.options.position + '"></div>'), 
        			self.container.append(self.wrapper)), 
        			self.alert = $('<div class="alert"></div>'), 
        			self.alert.addClass("alert-" + self.options.type), 
        			"bar" == self.options.style ? new BarNotification : "flip" == self.options.style ? new FlipNotification : "circle" == self.options.style ? new CircleNotification : ("simple" == self.options.style, new SimpleNotification), 
        					self.notification.append(self.alert), self.alert.on("closed.bs.alert", function() {
        						self.notification.remove(), self.options.onClosed()
        					}), this
    };
    Notification.VERSION = "1.0.0", Notification.prototype.show = function() {
        this.wrapper.prepend(this.notification), 
        this.options.onShown(), 
        0 != this.options.timeout && setTimeout(function() {
        	var $this = this;
            this.notification.fadeOut("slow", function() {
                $(this).remove(), 
                $this.options.onClosed()
            })
        }.bind(this), this.options.timeout)
    }, $.fn.appNotification = function(options) {
        return new Notification(this, options)
    }, $.fn.appNotification.defaults = {
        style: "simple",
        message: null,
        position: "top-right",
        type: "info",
        showClose: !0,
        timeout: 3e3,
        onShown: function() {},
        onClosed: function() {}
    }
}(window.jQuery),

function($) {
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
	
    var DashboardPage = function() {
        this.$body = $("body"),
        this.$container = '#widget-calls-chart',
        this.$statsPorltlet = $("#stats-portlet"),
        this.$signupPorltlet = $("#signup-portlet"),
        this.$callsPortlet = $("#calls-portlet"),
        this.$callsInPortlet = $("#calls-in-portlet"),
        this.$callsGraph = null,
        this.$callsInGraph = null
    };
    
    DashboardPage.prototype.craetePortlets = function() {
    	var $this = this;
    	//Stats
    	this.$statsPorltlet.portlet({
            progress: 'circle',
            progressColor: 'success',
            onRefresh: function() {
                setTimeout(function() {
                	$this.$statsPorltlet.portlet({
                        refresh: false
                    });
                }, 2000);
            }
        });
    	
    	//signups
    	this.$signupPorltlet.portlet({
            progress: 'circle',
            progressColor: 'success',
            onRefresh: function() {
                setTimeout(function() {
                	$this.$signupPorltlet.portlet({
                        refresh: false
                    });
                }, 2000);
            }
        });
    	
    	//calls
    	this.$callsPortlet.portlet({
            progress: 'circle',
            progressColor: 'success',
            onRefresh: function() {
                setTimeout(function() {
                	$this.$callsPortlet.portlet({
                        refresh: false
                    });
                }, 2000);
            }
        });
    	
    	//call in
    	this.$callsInPortlet.portlet({
            progress: 'circle',
            progressColor: 'success',
            onRefresh: function() {
            	
                setTimeout(function() {
                	$this.$callsInPortlet.portlet({
                        refresh: false
                    });
                }, 2000);
            }
        });
    },
    DashboardPage.prototype.getColor = function(color, opacity) {
        opacity = parseFloat(opacity) || 1;
        var elem = $(".pg-colors").length ? $(".pg-colors") : $('<div class="pg-colors"></div>').appendTo("body"),
            colorElem = elem.find('[data-color="' + color + '"]').length ? elem.find('[data-color="' + color + '"]') : $('<div class="bg-' + color + '" data-color="' + color + '"></div>').appendTo(elem),
            color = colorElem.css("background-color"),
            rgb = color.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/),
            rgba = "rgba(" + rgb[1] + ", " + rgb[2] + ", " + rgb[3] + ", " + opacity + ")";
        return rgba
    },
    DashboardPage.prototype.createCallsGraph = function() {
    	var $this = this;
    	var seriesData = [[],[],[]];
    	var random = new Rickshaw.Fixtures.RandomData(50);
        for (var i = 0; i < 50; i++) {
            random.addData(seriesData);
        }
        
        var graph = new Rickshaw.Graph({
            element: document.querySelector($this.$container),
            renderer: 'area',
            padding: {
                top: 0.5,
                bottom: 1
            },
            series: [{
                data: seriesData[0],
                color: $this.getColor('complete-light', .5),
                name: 'Calls'
            }, {
                data: seriesData[1],
                color: $this.getColor('success-light'),
                name: 'Pickups'
            }]
        });
        var y_axis = new Rickshaw.Graph.Axis.Y({
            graph: graph,
            orientation: 'right',
            tickFormat: function(y) {
                return y / 10;
            },
            element: document.querySelector('#widget-calls-chart_y_axis'),
        });
        var legend = new Rickshaw.Graph.Legend({
            graph: graph,
            element: document.querySelector('#widget-calls-chart-legend')
        });
        var shelving = new Rickshaw.Graph.Behavior.Series.Toggle({
            graph: graph,
            legend: legend
        });
        var hoverDetail = new Rickshaw.Graph.HoverDetail({
            graph: graph
        });
        setInterval(function() {
            random.removeData(seriesData);
            random.addData(seriesData);
            graph.update();
        }, 1000);
        d3.selectAll('#widget-calls-chart_y_axis .tick.major line').attr('x2', '7');
        d3.selectAll('#widget-calls-chart_y_axis .tick.major text').attr('x', '12');
        
        $(window).resize(function() {
            graph.configure({
                width: $($this.$container).width()
            });
            graph.render()
        });
        $($this.$container).data('chart', graph);
        $this.$callsGraph = graph;
    },
    DashboardPage.prototype.createCallInGraph = function() {
    	var $this = this;
    	
    	var data = [{
    		key: 'Call In',
    		area: true,
    		values: [
    		         [1, 100], [2, 80], [3, 130], [4, 100], [5,141],
    		         [6, 159], [7, 120], [8, 90], [9, 10]
    		]
    	}];
    	
    	nv.addGraph(function() {
    		var chart = nv.models.lineChart().x(function(d) {
    			return d[0]
    		}).y(function(d) {
    			return d[1]
    		}).color([$this.getColor('complete')]).forceY([0, 2]).useInteractiveGuideline(true).margin({
    				top: 60,
		            right: -10,
		            bottom: -10,
		            left: -10
    		}).showLegend(false);
    		
    		d3.select('.widget-calls-in-chart svg').datum(data).transition().duration(500).call(chart);
    		nv.utils.windowResize(function() {
    			chart.update();
    		});
    		
    		$('.widget-calls-in-chart').data('chart', chart);
    		$this.$callsInGraph = chart; 
    		return chart;
    	});
    	
    },
    DashboardPage.prototype.init = function() {
    	
    	this.craetePortlets(),
    	this.createCallsGraph(),
    	this.createCallInGraph()
    }, 
    $.DashboardPage = new DashboardPage, $.DashboardPage.Constructor = DashboardPage
    
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
    		$('body').appNotification({
                style: 'bar',
                message: msg,
                position: 'top',
                type: type
            }).show();
    	}
    	
    	//removing - hack
    	$("#s2id_ac-group-select").removeClass('form-control');
    }, 
    $.UserSettingPage = new UserSettingPage, $.UserSettingPage.Constructor = UserSettingPage
    
}(window.jQuery),




function($) {
    "use strict";
	
    var CouponPage = function() {
        this.$body = $("body") 
    };
    
    CouponPage.prototype.init = function() {
    	
    	
    }, 
    
    $.CouponPage = new CouponPage, $.CouponPage.Constructor = CouponPage
    
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
        this.$userselect = $("#select-user")
        this.$groupselect = $("#select-group")
        this.$broadcastselect = $("#select-broadcast")
        
    };
    
    ReportPage.prototype.init = function() {
 
     	var $this = this;
  
     	$.fn.select2 && $this.$userselect.select2({}).on("select2-opening", function() {
            $.fn.scrollbar && $(".select2-results").scrollbar({
                ignoreMobile: !1
            })
       });
     	
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
        this.$saveExcel = $("#saveasexcel"),
        this.$errorContainer = $("#show-notification"),
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
		    	var fieldLabelText = document.createTextNode("Select Field ");
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
		    	var amountLabelText = document.createTextNode("Enter Value ");
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
    	console.log("submiteddddddddddddddd");
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
    	console.log("END of submit")
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
    		
    		var hiddenfield = document.createElement("input");
    		hiddenfield.setAttribute("name", "save");
    		hiddenfield.setAttribute("value", true);
    		hiddenfield.setAttribute("type", "hidden");
    		$this.$userSearchForm.append(hiddenfield);
    		console.log("HELLO");
    	});
    	
        this.$userSearchForm.submit(function(event)  {
   
        	$.UserSearch.submit();
        });
    	
    	this.$advanceSearchLink.click(function() {
    		$.UserSearch.advanceSearchLink();
    		console.log("HELLOOOOOOOOOOO Final");
    		return false;
    	});
    	
    	this.$addFilterBtn.click(function() {
    		console.log("ADD Filter Button");
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
			console.log("HELLO");
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
    		$('body').appNotification({
                style: 'bar',
                message: msg,
                position: 'top',
                type: type
            }).show();
    	}
		
    },
    $.UserSearch = new UserSearch, $.UserSearch.Constructor = UserSearch
    
}(window.jQuery),

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
        this.$couponManagementPage = $("#coupon-container"),
        this.$reportPage = $("#report-container"),
        this.$addCouponPage = $("#add-coupon-container")
       
    };
    
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
    			//"ajax": typeof($table.attr("data-sourceurl") != 'undefined') == true ? $table.attr("data-sourceurl") : '/'
    			//"ajax": {
    			//	url: typeof($table.attr("data-sourceurl") != 'undefined') == true ? $table.attr("data-sourceurl") : '.',
    			//	type: 'POST'
    			//}
    	});
    },
    DashboardApp.prototype.initEasyPie = function() {
    	$('.pie-chart').easyPieChart({
    		easing: 'easeOutBounce',
    		onStep: function(from, to, percent) {
    			$(this.el).next('.p-value').text(Math.round(percent));
    		}
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
	
    DashboardApp.prototype.init = function() {
    	this.initTooltipPlugin(),
    	this.initSelect2Plugin(),
    	this.initDateTimePicker(),
    	this.initDataTable(),
    	this.initEasyPie(),
    	this.initSwitcheryPlugin(),
    	this.initFormGroupDefault();

    	//initiating 
    	if(this.$dashboardPage.length > 0)
    		$.DashboardPage.init();
    	//if(this.$userSearchPage.length > 0)
    	//	$.UserSearch.init();
    	if(this.$userSettingPage.length > 0)
    		$.UserSettingPage.init();
    	if(this.$couponManagementPage.length > 0)
    		$.CouponPage.init();
    	if(this.$addCouponPage.length > 0)
    		$.AddCouponPage.init();
    	if(this.$reportPage.length > 0)
    		$.ReportPage.init();
    	
    }, 
    $.DashboardApp = new DashboardApp, $.DashboardApp.Constructor = DashboardApp
}(window.jQuery),


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