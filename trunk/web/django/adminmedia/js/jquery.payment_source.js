/*
 * This module is for payment processing.
 */

jQuery(function($) {
	'use strict';

	//csrf
	var Csrf = {
		$csrfToken : null,
		init : function() {
			this.$csrfToken = this.getCookie('csrftoken');
			/* setting up ajax */
			$.ajaxSetup({
				beforeSend : function(xhr, settings) {
					if (!(/^http:./.test(settings.url) || /^https:./
							.test(settings.url))) {
						// Only send the token to relative URLs i.e. locally.
						xhr.setRequestHeader("X-CSRFToken", this.$csrfToken);
					}
				}
			});

			return this;
		},
		getToken : function() {
			if (typeof (this.$csrfToken) == 'undefined')
				this.$csrfToken = this.getCookie('csrftoken');
			return this.$csrfToken;
		},
		setHeader : function(xhr) {
			xhr.setRequestHeader("X-CSRFToken", this.$csrfToken);
		},
		getCookie : function(name) {
			var cookieValue = null;
			if (document.cookie && document.cookie != '') {
				var cookies = document.cookie.split(';');
				for (var i = 0; i < cookies.length; i++) {
					var cookie = jQuery.trim(cookies[i]);
					// Does this cookie string begin with the name we want?
					if (cookie.substring(0, name.length + 1) == (name + '=')) {
						cookieValue = decodeURIComponent(cookie
								.substring(name.length + 1));
						break;
					}
				}
			}
			return cookieValue;
		}
	};

	var RechargeApp = {
		$specialKeys : [ 18, 37, 38, 39, 40, 8, 20, 17, 46, 35, 13, 27, 36, 45, 144, 33, 34, 16, 9, 91 ], //special chars/keys

		$rechargeplanSel : $("#rechargeplan"),
		$rechargeplanLbl : $("#recharge_total_pr"),
		$memberRow : $("#memberrow"),
		$noMembersInp : $("#members"),
		$membersRadio : $("input[name=memberDurRadio]:radio"),
		$perMemberPrice : $("#permemberprice"),
		$memberTotalPrice : $("#membertotalprice"),
		$rcLbl : $("#reclbl"),

		$planCredits : [],
		$memberPrices : [],
		$memberTimeSlab : [],

		$rechargePrices : [],
		$rechargeCreditPlans : [],
		$selMemberTotalPrice : 0,
		$selMemberPrice : 0,
		$selPlanIdx : 0,
		$isUnlimitedPlan: false,

		$commonApp : null,
		init : function(commonapp_ins) {
			//initializing
			this.$specialKeys.push(8); //Backspace
			this.$specialKeys.push(16); //Shift
			this.$specialKeys.push(17); //Ctl
			this.$specialKeys.push(18); //Alt

			this.$rechargePrices = [ 999, 3499, 8599, 49999, 50000 ];
			this.$rechargeCreditPlans = [ 1500, 6000, 18000, 125000 ];

			this.$selRechargePrice = 3499;

			this.$memberPrices = [ 9, 8 ];
			this.$memberTimeSlab = [ 6, 12 ];

			this.$memberRow.hide();

			this.$commonApp = commonapp_ins;
			this.bindEvents();

			return this;
		},
		bindEvents : function() {
			this.$rechargeplanSel.on('change', this.changeRechargePrice.bind(this));
			this.$membersRadio.on('change', this.changeMemberPrice.bind(this));
			this.$noMembersInp.on('keyup', this.calMemberPrice.bind(this));
		},
		getRecCalculatedAmt : function() {
			return this.$selRechargePrice;
		},
		getCurrentSelectedPlanCredit : function() {
			var selPlanIdx = this.$rechargeplanSel.val();
			if (selPlanIdx == 4)
				return -1;
			return this.$rechargeCreditPlans[selPlanIdx];
		},
		getSelectedMember : function() {
			if(this.$isUnlimitedPlan)
				return this.$noMembersInp.val();
			else
				return -1;
		},
		getSelectedDuration : function() {
			return this.$noMembersInp.val();
		},
		getSelectedMemberDuration : function() {
			if(this.$isUnlimitedPlan)
				return ($("input[type='radio'][name='memberDurRadio']:checked").val() == 0 ? 6 : 12);
			else
				return null;
		},
		changeRechargePrice : function(event) {
			this.$selPlanIdx = this.$rechargeplanSel.val();

			if (this.$selPlanIdx == 4) {
				this.$memberRow.show();
				this.$selRechargePrice = 2700; //default selected
				this.$isUnlimitedPlan = true;
				this.$rcLbl.hide();
			} else {
				this.$memberRow.hide();
				this.$selRechargePrice = this.$rechargePrices[this.$selPlanIdx];
				this.$rechargeplanLbl.text(this.$commonApp.getFormattedNo(this.$selRechargePrice));
				this.$rcLbl.show();
			}
			this.$commonApp.changeTotal();
		},
		changeMemberPrice : function(event) {
			var selected_dur = $("input[type='radio'][name='memberDurRadio']:checked");
			if (selected_dur.length > 0) {
				this.$selMemberPrice = this.$memberPrices[selected_dur.val()];

				var selVal = this.$noMembersInp.val();
				var selIntVal = parseFloat(selVal);
				if (isNaN(selIntVal))
					selIntVal = 0.00;

				this.$perMemberPrice.text(this.$selMemberPrice.toFixed(2));

				this.$selRechargePrice = selIntVal * this.$selMemberPrice * this.$memberTimeSlab[selected_dur.val()];
				this.$memberTotalPrice.text(this.$commonApp.getFormattedNo(this.$selRechargePrice.toFixed(2)));
			}

			this.$commonApp.changeTotal();
		},
		calMemberPrice : function(e) {
			var keyCode = e.which ? e.which : e.keyCode;
			var ret = ((keyCode >= 48 && keyCode <= 57)
					|| (keyCode >= 96 && keyCode <= 105) || this.$specialKeys.indexOf(keyCode) != -1);
			var selVal = this.$noMembersInp.val();

			if (!ret)
				this.$noMembersInp.val(selVal.substring(0, selVal.length - 1));
			else
				this.changeMemberPrice();

			return ret;
		}
	};

	var GroupApp = {
		$groupRow : $("#groupRow"),
		$grpSize : $("#grpsize"),
		$norGroupLbl : $("#normal-grp"),
		$groupNoLbl : $("#group_no"),
		$durationRadio : $("input[name=durationRadio]:radio"),
		$grpPriceLbl : $("#grp_total_pr"),

		$groupPrices6Mon : [],
		$groupPrices12Mon : [],
		$selGroupPrice : 0,
		$selGrpIdx : 0,

		$commonApp : null,

		init : function(commonapp_ins) {
			this.$groupPrices6Mon = [ 1899, 3578, 5037, 6276, 7295, 8094, 8673, 9032, 9171, 9090 ];
			this.$groupPrices12Mon = [ 3798, 7156, 10074, 12552, 14590, 16188, 17346, 18064, 18342, 18180 ];
			
			this.setGrpCalculatedDefaultAmt();
			this.$grpSize.slider();
			this.$commonApp = commonapp_ins;
			this.bindEvents();

			return this;
		},
		getGrpCalculatedAmt : function() {
			return this.$selGroupPrice;
		},
		setGrpCalculatedDefaultAmt: function() {
			this.$selGroupPrice = 1899;
		},
		resetGrpCalculatedDefaultAmt: function() {
			this.$selGroupPrice = 0;
		},
		bindEvents : function() {
			this.$durationRadio.on('change', this.changeGroupPrice.bind(this));
			this.$grpSize.on('slide', this.changeGroupPrice.bind(this));
		},
		changeGroupPrice : function(e) {
			this.$selGrpIdx = this.$grpSize.slider('getValue');//parseInt(slideEvt.value);

			this.$groupNoLbl.text(this.$selGrpIdx);

			var selected_dur = $("input[type='radio'][name='durationRadio']:checked");
			if (selected_dur.length > 0) {
				if (selected_dur.val() == 1) {
					if (this.$selGrpIdx >= 10)
						this.$selGroupPrice = this.$selGrpIdx * 900;
					else
						this.$selGroupPrice = this.$groupPrices6Mon[this.$selGrpIdx - 1];
				} else {
					if (this.$selGrpIdx >= 10)
						this.$selGroupPrice = this.$selGrpIdx * 1800;
					else
						this.$selGroupPrice = this.$groupPrices12Mon[this.$selGrpIdx - 1];
				}
			}
			this.$grpPriceLbl.text(this.$commonApp.getFormattedNo(this.$selGroupPrice));

			this.$commonApp.changeTotal();
		},
		getSelectedGroup : function() {
			return this.$grpSize.slider('getValue');
		},
		getGroupDuration : function() {
			return ($("input[type='radio'][name='durationRadio']:checked").val() == 1 ? 6 : 12);
		}
	};

	var CouponApp = {
		$couponValInp : $("#coupon"),
		$couponErrorLbl : $("#couponErrorLbl"),
		$applyBtn : $("#applyBtn"),
		$urlInput: $("#coupon_url"),

		$commonApp : null,

		init : function(commonapp_ins) {
			this.$commonApp = commonapp_ins;
			this.bindEvents();
			return this;
		},
		bindEvents : function() {
			this.$couponValInp.on('dblclick', this.enableCoupon.bind(this));
			this.$applyBtn.on('click', this.applyCoupon.bind(this));
		},
		enableCoupon : function() {
			this.$applyBtn.button('reset');
			this.$couponValInp.removeAttr('readonly');
			this.$couponValInp.val('');
			this.$couponErrorLbl.html('');
			this.$commonApp.changeTotal();
		},
		showError : function(error) {
			this.$couponErrorLbl.html(error);
			this.$couponErrorLbl.removeClass("label-success-c");
			this.$couponErrorLbl.addClass("label-error");
		},
		applyCoupon : function(event) {
			event.preventDefault();

			this.$applyBtn.button('loading');
			var famt = this.$commonApp.getCurrentAmount();

			if (famt < 0) {
				this.$couponErrorLbl.text("Total amount should be greater than 0");
				this.$couponErrorLbl.addClass("label-error");
				this.$applyBtn.button('reset');
			} else if (this.$couponValInp.val() == '' || typeof (this.$couponValInp.val()) == 'undefined') {
				this.$couponValInp.addClass('field-error');
				this.$couponErrorLbl.text("Please enter coupon code");
				this.$couponErrorLbl.addClass("label-error");
				this.$applyBtn.button('reset');
			} else {
				this.$couponValInp.removeClass('field-error');

				var $this = this;
				$.ajax({
					type : "POST",
					withCredentials : true,
					async : false,
					url : $this.$urlInput.val(),
					headers : {
						csrftoken : this.$commonApp.getCSRFToken()
					},
					data : {
						csrfmiddlewaretoken : this.$commonApp.getCSRFToken(),
						code : this.$couponValInp.val(),
						amount : famt
					},
					success : function(json) {
						if (typeof (json.error) != 'undefined' && json.error != '') {
							$this.$couponErrorLbl.html(json.error);
							$this.$couponErrorLbl.removeClass("label-success-c");
							$this.$couponErrorLbl.addClass("label-error");
							$this.$couponValInp.addClass('field-error');
							$this.$commonApp.setNewAmount(json.new_amount);
						} else {
							$this.$couponErrorLbl.html(json.success);
							$this.$couponErrorLbl.removeClass("label-error");
							$this.$couponErrorLbl.addClass("label-success-c");
							$this.$couponValInp.removeClass('field-error');
							$this.$couponValInp.attr('readonly', 'readonly');
							$this.$commonApp.setNewAmount(json.new_amount);
						}
						$this.$applyBtn.button('reset');
						return false;
					},
					error : function(jqxhr, textStatus, errorThrown) {
						console.log(jqxhr);
						console.log(textStatus);
						console.log(errorThrown);
						$this.$applyBtn.button('reset');
					}
				});
				return false;
			}
			return false;
		}
	};

	var CommonApp = {
		$payBtn : $("#btnpay"),
		$secureAmt : $("#id_secure_hash"),
		$amtHidden : $("#id_amount"),
		$totalPriceBtn : $("#total_prbtn"),
		$refNoHidden : $("#id_reference_no"),
		$form : $("#frmTransaction"),
		$urlInput: $("#hash_url"),
		$choiceCheckboxes : $("input[name=choiceCheckbox]"),
		$buyMessagesRadio: $("#buy_messages"),
		$buyGroupsRadio: $("#buy_groups"),
		$option: null,
		$isGroupEnabled: true,
		$isMessageEnabled: true,
		$csrf : Csrf.init(),
		$couponApp : null,
		$groupApp : null,
		$rechargeApp : null,

		init : function() {
			//initializing
			this.$couponApp = CouponApp.init(this);
			this.$groupApp = GroupApp.init(this);
			this.$rechargeApp = RechargeApp.init(this);
			this.$amtHidden.val(5398);
			this.$option = 3;
			this.bindEvents();
		},
		bindEvents : function() {
			this.$payBtn.on('click', this.getSecureHash.bind(this));
			this.$choiceCheckboxes.on('change', this.changePurchaseChoice.bind(this));
		},
		changePurchaseChoice: function(e) {
			var target_sec = $($(e.target).attr('target'));
			if($(e.target).is(":checked")) {
				target_sec.fadeIn(500);
			} else {
				target_sec.fadeOut(500);
			}
			
			//resetting selected prices
			this.$isGroupEnabled = this.$buyGroupsRadio.is(":checked");
			this.$isMessageEnabled = this.$buyMessagesRadio.is(":checked");
			
			if(!this.$buyMessagesRadio.is(":checked") && !this.$buyGroupsRadio.is(":checked")) {
				this.$buyMessagesRadio.prop( "checked", true );
				this.$buyMessagesRadio.trigger("change");
				this.$isMessageEnabled = true;
			}
			this.changeTotal();
		},
		getCurrentAmount : function() {
			this.changeTotal();
			return this.$amtHidden.val();
		},
		getSecureHash : function(event) {
			event.preventDefault();
			var credits = 0, groups = 0;
			if(this.$isGroupEnabled && this.$isMessageEnabled) {
				credits = this.$rechargeApp.getCurrentSelectedPlanCredit();
				groups = this.$groupApp.getSelectedGroup();
				this.$option = 3;
			}
			else if(this.$isGroupEnabled) {
				groups = this.$groupApp.getSelectedGroup();
				this.$option = 1;
			}
			else {
				credits = this.$rechargeApp.getCurrentSelectedPlanCredit();
				this.$option = 2;
			}
				
			var $this = this;
			$.ajax({
						type : "POST",
						withCredentials : true,
						async : false,
						url : $this.$urlInput.val(),
						headers : {
							csrftoken : this.$csrf.getToken()
						},
						data : {
							csrfmiddlewaretoken : $this.$csrf.getToken(),
							amount : $this.$amtHidden.val(),
							refrenceno : $this.$refNoHidden.val(),
							credits : credits,
							nogroups : groups,
							groupduration : $this.$groupApp.getGroupDuration(),
							nomembers : $this.$rechargeApp.getSelectedMember(),
							memberduration : $this.$rechargeApp.getSelectedMemberDuration(),
							option : $this.$option
						},
						success : function(json) {
							if (typeof (json.error) != 'undefined' && json.error != '') {
								$this.$couponApp.showError(json.error);
								event.stopPropagation();
							} else {
								$this.$secureAmt.val((json.token));
								$this.$form.submit();
							}
						},
						error : function(jqxhr, textStatus, errorThrown) {
							console.log(jqxhr);
							console.log(textStatus);
							console.log(errorThrown);
							$this.$applyBtn.button('reset');
							event.stopPropagation();
							return false;
						}
					});
		},
		getFormattedNo : function(number) {
			var num = number.toString();
			var afterPoint = '';
			if (num.indexOf('.') > 0)
				afterPoint = num.substring(num.indexOf('.'), num.length);
			num = Math.floor(num);
			num = num.toString();
			var lastThree = num.substring(num.length - 3);
			var otherNumbers = num.substring(0, num.length - 3);
			if (otherNumbers != '')
				lastThree = ',' + lastThree;
			return (otherNumbers.replace(/\B(?=(\d{2})+(?!\d))/g, ",") + lastThree + afterPoint);
		},
		changeTotal : function() {
			var famt = 0.00;
			if(this.$isMessageEnabled)
				famt += this.$rechargeApp.getRecCalculatedAmt();
			if(this.$isGroupEnabled)
				famt += this.$groupApp.getGrpCalculatedAmt();
			
			this.$totalPriceBtn.text(famt);
			this.$amtHidden.val(famt.toFixed(2));
		},
		setNewAmount : function(new_amount) {
			this.$totalPriceBtn.text(new_amount);
			this.$amtHidden.val(new_amount);
		},
		getCSRFToken : function() {
			return this.$csrf.getToken();
		}
	};

	//starting
	CommonApp.init();
});