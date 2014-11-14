package org.otalo.ao.client;

import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Set;

import org.otalo.ao.client.JSONRequest.AoAPI;
import org.otalo.ao.client.model.BaseModel;
import org.otalo.ao.client.model.Forum;
import org.otalo.ao.client.model.Forum.ForumStatus;
import org.otalo.ao.client.model.JSOModel;
import org.otalo.ao.client.model.Line;
import org.otalo.ao.client.model.Membership;
import org.otalo.ao.client.model.Membership.MembershipStatus;
import org.otalo.ao.client.model.User;

import com.google.gwt.cell.client.ActionCell;
import com.google.gwt.cell.client.CheckboxCell;
import com.google.gwt.cell.client.EditTextCell;
import com.google.gwt.cell.client.FieldUpdater;
import com.google.gwt.cell.client.TextCell;
import com.google.gwt.cell.client.ValueUpdater;
import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.Style.Unit;
import com.google.gwt.event.dom.client.ChangeEvent;
import com.google.gwt.event.dom.client.ChangeHandler;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.dom.client.KeyCodes;
import com.google.gwt.event.logical.shared.CloseEvent;
import com.google.gwt.event.logical.shared.CloseHandler;
import com.google.gwt.event.logical.shared.SelectionEvent;
import com.google.gwt.event.logical.shared.SelectionHandler;
import com.google.gwt.i18n.client.DateTimeFormat;
import com.google.gwt.resources.client.ImageResource;
import com.google.gwt.user.cellview.client.Column;
import com.google.gwt.user.cellview.client.ColumnSortEvent;
import com.google.gwt.user.cellview.client.ColumnSortList;
import com.google.gwt.user.cellview.client.ColumnSortList.ColumnSortInfo;
import com.google.gwt.user.cellview.client.DataGrid;
import com.google.gwt.user.cellview.client.Header;
import com.google.gwt.user.cellview.client.SimplePager;
import com.google.gwt.user.cellview.client.SimplePager.TextLocation;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.DecoratedTabPanel;
import com.google.gwt.user.client.ui.DialogBox;
import com.google.gwt.user.client.ui.FileUpload;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteEvent;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteHandler;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HasAlignment;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.Hidden;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.PopupPanel;
import com.google.gwt.user.client.ui.RadioButton;
import com.google.gwt.user.client.ui.TextArea;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.view.client.AsyncDataProvider;
import com.google.gwt.view.client.DefaultSelectionEventManager;
import com.google.gwt.view.client.HasData;
import com.google.gwt.view.client.MultiSelectionModel;
import com.google.gwt.view.client.Range;
import com.google.gwt.view.client.SelectionModel;
import com.google.web.bindery.event.shared.HandlerRegistration;

public class ManageGroups extends Composite {
	private DecoratedTabPanel tabPanel = new DecoratedTabPanel();
	private Hidden groupid, memberStatus, membersToUpdate;
	private Button saveButton, cancelButton, addMembersButton, cancelAddMembers, deleteButton;
	private ListBox languageBox, deliveryBox, inputBox, statusFilterBox, reports, month, year, backupsBox, maxInputLengthBox;
	private DataGrid<Membership> memberTable, joinsTable;
	private DataGrid<Broadcast> reportTable;
	private FormPanel manageGroupsForm;
	private VerticalPanel addMembersPanel, namesPanel;
	private HorizontalPanel memberControls;
	private FlexTable greetingMessage;
	private SimplePager pager;
	private TextBox groupNameText, emailText, senderText;
	private HandlerRegistration submitHandler = null;
	private AreYouSureDialog confirm;
	private TextArea numbersArea, namesArea, publishersArea;
	private Label groupNumber, maxInputLabel;
	private HTML creditsLabel;
	private RadioButton inboundOff, inboundMemsOnly, inboundAll;
	private int reportStartIndex = 0, membersStartIndex = 0;
	private CheckBox welcomeSMS, forwardAllowed;
	
	private Forum group;
	private Line line;
	
	public interface Images extends Fora.Images {
		ImageResource group();
	}
	
	public ManageGroups(Images images) {
		VerticalPanel outer = new VerticalPanel();
		outer.setSize("100%","100%");
		
		manageGroupsForm = new FormPanel();
    manageGroupsForm.setMethod(FormPanel.METHOD_POST);
		
    /**************************************************
		 * 
		 *  Top Panel (group selection and tabs)
		 *  
		 *************************************************/
 		VerticalPanel memberPanel = new VerticalPanel();
		memberPanel.setSize("100%", "100%");
		VerticalPanel settingsPanel = new VerticalPanel();
		settingsPanel.setSize("100%", "100%");
		VerticalPanel joinsPanel = new VerticalPanel();
		joinsPanel.setSize("100%", "100%");
		VerticalPanel reportsPanel = new VerticalPanel();
		reportsPanel.setSize("100%", "100%");
		
		tabPanel.setSize("100%", "100%");
		tabPanel.add(memberPanel, "Members");
		tabPanel.add(joinsPanel, "Join Requests");
		tabPanel.add(reportsPanel, "Reports");
		tabPanel.add(settingsPanel, "Settings");
		tabPanel.addSelectionHandler(new SelectionHandler<Integer>() {
			
			public void onSelection(SelectionEvent<Integer> event) {
				int tabId = event.getSelectedItem();
        if (tabId == 0) 
        {
        	membersStartIndex = 0;
        	statusFilterBox.setSelectedIndex(0);
        	memberTable.getColumnSortList().clear();
        	// show loading data icon
        	// (from http://www.quora.com/Google-Web-Toolkit-GWT/How-do-I-change-loading-state-of-a-GWT-celltable)
        	memberTable.setVisibleRangeAndClearData(new Range(membersStartIndex, memberTable.getPageSize()), true);
	        showMemberTable();
        }
        else if (tabId == 1)
        {
        	
        	membersStartIndex = 0;
        	joinsTable.getColumnSortList().clear();
        	joinsTable.setVisibleRangeAndClearData(new Range(membersStartIndex, joinsTable.getPageSize()), true);
        }
        else if (tabId == 2)
        {
        	reportStartIndex = 0;
        	reportTable.setVisibleRangeAndClearData(new Range(reportStartIndex, reportTable.getPageSize()), true);
        }
			}
		});
		
		/**************************************************
		 * 
		 *  Members Tab
		 *  
		 *************************************************/
		memberStatus = new Hidden();
		memberStatus.setName("memberstatus");
		membersToUpdate = new Hidden();
		membersToUpdate.setName("memberids");
		
		// top-level controls
		memberControls = new HorizontalPanel();
		memberControls.setWidth("800px");
		memberControls.setSpacing(10);
		Button removeMembers = new Button("Remove from group");
		Anchor addMembers = new Anchor("Add members");
		addMembers.addClickHandler(new ClickHandler() {
			
			public void onClick(ClickEvent event) {
				showAddMembersView();
			}
			
		});
		Label filterLabel = new Label("Filter By");
		statusFilterBox = new ListBox();
		statusFilterBox.addItem("", "-1");
		statusFilterBox.addItem(Membership.MembershipStatus.SUBSCRIBED.getTxtValue(), String.valueOf(MembershipStatus.SUBSCRIBED.getCode()));
		statusFilterBox.addItem(Membership.MembershipStatus.UNSUBSCRIBED.getTxtValue(), String.valueOf(MembershipStatus.UNSUBSCRIBED.getCode()));
		
		statusFilterBox.addChangeHandler(new ChangeHandler() {

			public void onChange(ChangeEvent event) {
				membersStartIndex = 0;
				memberTable.setVisibleRangeAndClearData(new Range(membersStartIndex, memberTable.getPageSize()), true);
			}
		});
		
		memberControls.add(removeMembers);
		memberControls.add(addMembers);
				
		memberControls.setHorizontalAlignment(HasAlignment.ALIGN_RIGHT);
		HorizontalPanel filterPanel = new HorizontalPanel();
		filterPanel.add(filterLabel);
		filterPanel.add(statusFilterBox);
		filterPanel.setSpacing(5);
		memberControls.add(filterPanel);
		
		// Member Grid
		memberTable = new DataGrid<Membership>();
		memberTable.setSize("850px", "360px");
		//memberTable.setRowCount(50, false);
		memberTable.setPageSize(50);
		
		// Add a selection model so we can select cells.
    final MultiSelectionModel<Membership> selectionModel = new MultiSelectionModel<Membership>();
    memberTable.setSelectionModel(selectionModel, DefaultSelectionEventManager.<Membership> createCheckboxManager());
    
    // Create a Pager to control the table.
    SimplePager.Resources pagerResources = GWT.create(SimplePager.Resources.class);
    pager = new MembersPager(TextLocation.CENTER, pagerResources, false, 0, true);
    pager.setPageSize(50);
    pager.setDisplay(memberTable);
    //pager.setRangeLimited(false);

    // Initialize the columns.
    initTableColums(selectionModel);
    
    membersDataProvider.addDataDisplay(memberTable);
    memberTable.addColumnSortHandler(new ColumnSortEvent.Handler() {
			
			public void onColumnSort(ColumnSortEvent event) {
				String code = statusFilterBox.getValue(statusFilterBox.getSelectedIndex());
				if (!code.equals("-1"))
				{
					MembershipStatus status[] = {MembershipStatus.getStatus(Integer.valueOf(code))};
					loadMembers(status);
				}
				else
					loadMembers();
				
			}
		});
    
    memberPanel.add(memberControls);
    memberPanel.add(memberTable);
    memberPanel.setHorizontalAlignment(HasAlignment.ALIGN_CENTER);
    memberPanel.add(pager);
    removeMembers.addClickHandler(new UpdateMemberClickHandler(memberTable, "Are you sure you want to remove selected members from your group?", MembershipStatus.DELETED, "Members removed!"));
    
    /**************************************************
		 * 
		 * Add Membership Interface
		 *  
		 *************************************************/  
    creditsLabel = new HTML();
    VerticalPanel creditsPanel = new VerticalPanel();
    creditsPanel.setSpacing(5);
    creditsPanel.add(creditsLabel);
    Label numbersLabel = new Label("Enter 10-digit numbers, one per line. Pasting from a spreadsheet is OK.");
    numbersLabel.setWordWrap(true);
    Anchor addNamesLink = new Anchor("Add Names");
		addNamesLink.addClickHandler(new ClickHandler() {
			
			public void onClick(ClickEvent event) {
					namesPanel.setVisible(true);
			}
				
		});
    Label numbersHelp = new Label("Each person will receive an SMS welcoming them to your group and reminding them that they can unsubscribe any time.");
    numbersHelp.setWordWrap(true);
    numbersHelp.setStyleName("helptext");
    numbersArea = new TextArea();
    numbersArea.setName("numbers");
		numbersArea.setSize("600px", "100px");
		VerticalPanel numbersPanel = new VerticalPanel();
		numbersPanel.setSpacing(5);
    HorizontalPanel numsLblPanel = new HorizontalPanel();
    numsLblPanel.setWidth("100%");
    numsLblPanel.add(numbersLabel);
    numsLblPanel.setHorizontalAlignment(HasAlignment.ALIGN_RIGHT);
    numsLblPanel.add(addNamesLink);
		numbersPanel.add(numsLblPanel);
		numbersPanel.add(numbersArea);
		numbersPanel.add(numbersHelp);
		
		Label namesLabel = new Label("Enter names one per line. Pasting from a spreadsheet is OK.");
		namesLabel.setWordWrap(true);
    Label namesHelp = new Label("Match the order of names to the phone numbers box above. Skip a line for unknown names.");
    namesHelp.setWordWrap(true);
    namesHelp.setStyleName("helptext");
    namesArea = new TextArea();
    namesArea.setName("names");
    namesArea.setSize("600px", "100px");
    namesPanel = new VerticalPanel();
    namesPanel.setSpacing(5);
    namesPanel.add(namesLabel);
    namesPanel.add(namesArea);
    namesPanel.add(namesHelp);
    namesPanel.setVisible(false);
    
    welcomeSMS = new CheckBox();
    welcomeSMS.setName("welcomeSMS");
    welcomeSMS.setText("Send Welcome SMS");
		
    memberPanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_LEFT);
    addMembersPanel = new VerticalPanel();
    addMembersPanel.setSpacing(10);
    addMembersPanel.add(creditsPanel);
    addMembersPanel.add(new HTML("<br />"));
    addMembersPanel.add(numbersPanel);
    addMembersPanel.add(namesPanel);
    addMembersPanel.add(welcomeSMS);
		
		addMembersButton = new Button("Add Members", new ClickHandler() {
			public void onClick(ClickEvent event) {
				if (numbersArea.getValue() == null || "".equals(numbersArea.getValue()))
				{
					ConfirmDialog nonumbers = new ConfirmDialog("Please specify phone numbers in the given area.");
					nonumbers.show();
					nonumbers.center();
				}
				else
				{
	      	setClickedButton();
	      	if (submitHandler != null)
	      	{
	      		submitHandler.removeHandler();
	      		submitHandler = null;
	      	}
	      	submitHandler = manageGroupsForm.addSubmitCompleteHandler(new AddMembersComplete());
	      	manageGroupsForm.setAction(JSONRequest.BASE_URL + AoAPI.ADD_MEMBERS);
	      	manageGroupsForm.setEncoding(FormPanel.ENCODING_URLENCODED);
	      	manageGroupsForm.submit();
				}
    	}
    });
		
		cancelAddMembers = new Button("Cancel");
		cancelAddMembers.addClickHandler(new ClickHandler(){
			public void onClick(ClickEvent event) {
					tabPanel.selectTab(0);
			}
			
		});
		
		HorizontalPanel addMembersButtonsPanel = new HorizontalPanel();
		addMembersButtonsPanel.setSpacing(10);
		addMembersButtonsPanel.add(cancelAddMembers);
		addMembersButtonsPanel.add(addMembersButton);
		addMembersPanel.setHorizontalAlignment(HasAlignment.ALIGN_RIGHT);
		addMembersPanel.add(addMembersButtonsPanel);
		addMembersPanel.setVisible(false);
		
		memberPanel.add(addMembersPanel);
		
		/**************************************************
		 * 
		 *  Join Requests Tab
		 *  
		 *************************************************/
		// top-level controls
		HorizontalPanel joinControls = new HorizontalPanel();
		joinControls.setSpacing(10);
		Button approveMembers = new Button("Approve requests");
		Button rejectMembers = new Button("Reject requests");
		
		joinControls.add(approveMembers); 
		joinControls.add(rejectMembers); 
		
		joinsTable = new DataGrid<Membership>();
		joinsTable.setSize("850px", "360px");
		joinsTable.setRowCount(50, true);
		
    joinsTable.setSelectionModel(selectionModel, DefaultSelectionEventManager.<Membership> createCheckboxManager());

    // Create a Pager to control the table.
    MembersPager joinsPager = new MembersPager(TextLocation.CENTER, pagerResources, false, 0, true);
    joinsPager.setDisplay(joinsTable);

    // Initialize the columns.
    initJoinTableColums(selectionModel);
    
    membersDataProvider.addDataDisplay(joinsTable);
    joinsTable.addColumnSortHandler(new ColumnSortEvent.Handler() {
			
			public void onColumnSort(ColumnSortEvent event) {
				loadJoinRequests();
				
			}
		});
    
    approveMembers.addClickHandler(new UpdateMemberClickHandler(joinsTable, "Are you sure you want to approve these requests?", MembershipStatus.SUBSCRIBED, "Members joined!"));
		rejectMembers.addClickHandler(new UpdateMemberClickHandler(joinsTable, "Are you sure you want to reject these requests?", MembershipStatus.DELETED, "Members rejected!"));
    joinsPanel.add(joinControls);
    joinsPanel.add(joinsTable);
    joinsPanel.setHorizontalAlignment(HasAlignment.ALIGN_CENTER);
    joinsPanel.add(joinsPager);
		
		/**************************************************
		 * 
		 *  Reports Tab
		 *  
		 *************************************************/
				
		// Reports Grid
		reportTable = new DataGrid<Broadcast>();
		reportTable.setSize("850px", "360px");
		
		reportTable.setPageSize(10);
    
    // Create a Pager to control the table.
    MembersPager reportspager = new MembersPager(TextLocation.CENTER, pagerResources, false, 0, true);
    reportspager.setPageSize(50);
    reportspager.setDisplay(reportTable);

    // Initialize the columns.
    initReportColumns();

    // Add the member table to the adapter in the database.
    reportsDataProvider.addDataDisplay(reportTable);
    //reportsDataProvider.updateRowData(0, null);
    
    reports = new ListBox();
    reports.addItem("Call-in report", "callin");
    reports.addItem("Forwards report", "forward");
    String months[] = {"Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"};
    month = new ListBox();
    for (int i=0; i<months.length; i++)
    {
    	month.addItem(months[i], String.valueOf(i+1));
    }
    DateTimeFormat dtf = DateTimeFormat.getFormat("yyyy");
    String currentYearStr = dtf.format(new Date());
    int currentYear = Integer.valueOf(currentYearStr);
    
    year = new ListBox();
    for (int i=currentYear; 2012<=i; i--)
    {
    	year.addItem(String.valueOf(i));
    }
    Button downloadReport = new Button("Download");
    downloadReport.addClickHandler(new ClickHandler() {

			public void onClick(ClickEvent event) {
				String params = "/?reporttype=" + reports.getValue(reports.getSelectedIndex()) + "&month=" + month.getValue(month.getSelectedIndex()) + "&year=" + year.getValue(year.getSelectedIndex());
				Window.open(JSONRequest.BASE_URL+AoAPI.DOWNLOAD_STREAM_REPORT + group.getId() + params, "Download Report", "");
				
			}
		});
    
    HorizontalPanel callinReportPanel = new HorizontalPanel();
    callinReportPanel.setSpacing(8);
    callinReportPanel.add(reports);
    callinReportPanel.add(new Label("for"));
    callinReportPanel.add(month);
    callinReportPanel.add(year);
    callinReportPanel.add(downloadReport);
    
    reportsPanel.setSpacing(15);
    reportsPanel.add(reportTable);
    reportsPanel.setHorizontalAlignment(HasAlignment.ALIGN_CENTER);
    reportsPanel.add(reportspager);
    reportsPanel.setHorizontalAlignment(HasAlignment.ALIGN_LEFT);
    reportsPanel.add(callinReportPanel);
    
    /**************************************************
		 * 
		 *  Settings Tab
		 *  
		 *************************************************/
    Label groupNumberLabel = new Label("Group Number");
    groupNumber = new Label();
    Label groupNameLabel = new Label("Group Name");
    groupNameText = new TextBox();
    groupNameText.setName("groupname");
    
    Label languageLabel = new Label("Language");
    languageBox = new ListBox();
    languageBox.setName("language");
    // hard-coding for now; stay consistent with forms.py:createacctform
    languageBox.addItem("Hindi", "hin");
    languageBox.addItem("Gujarati", "guj");
    languageBox.addItem("Tamil", "tam");
    languageBox.addItem("Kannada", "kan");
    languageBox.addItem("English", "eng");
    
    Label deliveryLabel = new Label("Delivery Type");
    deliveryBox = new ListBox();
    deliveryBox.setName("deliverytype");
    // hard-coding for now; stay consistent with forms.py:createacctform
    deliveryBox.addItem("Call Only", String.valueOf(Forum.ForumStatus.BCAST_CALL.getCode()));
    deliveryBox.addItem("Call + SMS", String.valueOf(Forum.ForumStatus.BCAST_CALL_SMS.getCode()));
    deliveryBox.addItem("SMS Only", String.valueOf(Forum.ForumStatus.BCAST_SMS.getCode()));
    Label deliveryHelp = new Label("IMPORTANT: SMSs cost half credit per recipient in addition to the call charge.");
    deliveryHelp.setStyleName("helptext");
    HorizontalPanel deliveryPanel = new HorizontalPanel();
    deliveryPanel.setSpacing(5);
    deliveryPanel.add(deliveryBox);
    deliveryPanel.add(deliveryHelp);
    
    Label inputTypeLabel = new Label("Response Type");
    inputBox = new ListBox();
    inputBox.setName("inputtype");
    inputBox.addItem("Touchtone", "0");
    inputBox.addItem("Voice", "1");
    
    maxInputLabel = new Label("Max Number of Digits");
    maxInputLengthBox = new ListBox();
    maxInputLengthBox.setName("max_input_len");
    for(int i=1; i < 11; i++)
		{
    	maxInputLengthBox.addItem(String.valueOf(i));
		}
    
    inputBox.addChangeHandler(new ChangeHandler() {
			
			public void onChange(ChangeEvent event) {
				int idx = inputBox.getSelectedIndex();
				if (idx == 0)
				{
					// touchtone
					maxInputLabel.setVisible(true);
					maxInputLengthBox.setItemSelected(0, true);
					maxInputLengthBox.setVisible(true);
					
				}
				else
				{
					// voice
					maxInputLabel.setVisible(false);
					maxInputLengthBox.setVisible(false);
				}
				
			}
		});
    HorizontalPanel maxInputControls = new HorizontalPanel();
    maxInputControls.setSpacing(8);
    maxInputControls.add(inputBox);
    maxInputControls.add(maxInputLabel);
    maxInputControls.add(maxInputLengthBox);
    
    Label freeInboundLabel = new Label("Missed Call");
    inboundOff = new RadioButton("freeinbound", "Off");
    inboundOff.setFormValue("inboundoff");
    inboundMemsOnly = new RadioButton("freeinbound", "Members Only");
    inboundMemsOnly.setFormValue("inboundmemsonly");
    inboundAll = new RadioButton("freeinbound", "All");
    inboundAll.setFormValue("inboundall");
    HorizontalPanel inboundButtons = new HorizontalPanel();
    inboundButtons.setSpacing(5);
    inboundButtons.add(inboundOff);
    inboundButtons.add(inboundMemsOnly);
    inboundButtons.add(inboundAll);
    
    Label backupsLabel = new Label("Backup Calls");
    backupsBox = new ListBox();
    backupsBox.setName("backup_calls");
    backupsBox.addItem("0");
    backupsBox.addItem("1");
    backupsBox.addItem("2");
    
    Label forwardLabel = new Label("Allow Forwarding");
    forwardAllowed = new CheckBox();
    forwardAllowed.setName("forward");
    
    Label emailLabel = new Label("Email Address");
    emailText = new TextBox();
    emailText.setName("email");
    Label emailHelp = new Label("Daily Digest will be sent here");
    emailHelp.setStyleName("helptext");
    HorizontalPanel emailPanel = new HorizontalPanel();
    emailPanel.setSpacing(5);
    emailPanel.add(emailText);
    emailPanel.add(emailHelp);
    
    Label senderLabel = new Label("Sender Name");
    senderText = new TextBox();
    senderText.setName("sendername");
    Label senderHelp = new Label("This name appears as the sender on SMSs");
    senderHelp.setStyleName("helptext");
    HorizontalPanel senderPanel = new HorizontalPanel();
    senderPanel.setSpacing(5);
    senderPanel.add(senderText);
    senderPanel.add(senderHelp);
    
    Label publishersLabel = new Label("Multiple Publishers");
    publishersArea = new TextArea();
    publishersArea.setName("publishers");
    publishersArea.setSize("95px", "90px");
    Label publishersHelp = new HTML("Specify other phone numbers from which messages can be posted. <br /> Enter one 10-digit number per line.");
    publishersHelp.setStyleName("helptext");
    HorizontalPanel pubsPanel = new HorizontalPanel();
    pubsPanel.setSpacing(5);
    pubsPanel.add(publishersArea);
    pubsPanel.add(publishersHelp);
    
    Label greetingLabel = new Label("Greeting Message");
    greetingMessage = new FlexTable();
    //greetingMessage.setSpacing(5);
    FileUpload uploadGreeting = new FileUpload();
    uploadGreeting.setName("greetingmessage");
    uploadGreeting.setTitle("Upload greeting");
    greetingMessage.setWidget(0, 1, uploadGreeting);
    
    deleteButton = new Button("Delete group", new ClickHandler() {
      public void onClick(ClickEvent event) {
      	confirm = new AreYouSureDialog("Are you sure you want to delete this group?");
				confirm.show();
				confirm.center();
				
				confirm.addCloseHandler(new CloseHandler<PopupPanel>() {
					public void onClose(CloseEvent<PopupPanel> event) {
						if (confirm.isConfirmed())
						{
			      	setClickedButton();
			      	if (submitHandler != null)
			      	{
			      		submitHandler.removeHandler();
			      		submitHandler = null;
			      	}
			      	submitHandler = manageGroupsForm.addSubmitCompleteHandler(new DeleteComplete());
			      	manageGroupsForm.setAction(JSONRequest.BASE_URL + AoAPI.DELETE_GROUP);
			      	manageGroupsForm.setEncoding(FormPanel.ENCODING_URLENCODED);
			      	manageGroupsForm.submit();
						}
					}
				});
      }
    });
    
		saveButton = new Button("Save", new ClickHandler() {
      public void onClick(ClickEvent event) {
      	setClickedButton();
      	if (submitHandler != null)
      	{
      		submitHandler.removeHandler();
      		submitHandler = null;
      	}
      	submitHandler = manageGroupsForm.addSubmitCompleteHandler(new SettingsComplete());
      	manageGroupsForm.setAction(JSONRequest.BASE_URL + AoAPI.UPDATE_GROUP_SETTINGS);
      	manageGroupsForm.setEncoding(FormPanel.ENCODING_MULTIPART);
      	manageGroupsForm.submit();
      }
    });
		
		cancelButton = new Button("Cancel");
		cancelButton.addClickHandler(new ClickHandler(){
			public void onClick(ClickEvent event) {
					reset(line, group);
			}
			
		});
		
		int row = 0;
		FlexTable settingsTable = new FlexTable();
		settingsTable.setCellSpacing(10);
		settingsTable.setWidget(row, 0, groupNumberLabel);
		settingsTable.setWidget(row++, 1, groupNumber);
		settingsTable.setWidget(row, 0, groupNameLabel);
		settingsTable.setWidget(row++, 1, groupNameText);
		settingsTable.setWidget(row, 0, languageLabel);
		settingsTable.setWidget(row++, 1, languageBox);
		settingsTable.setWidget(row, 0, deliveryLabel);
		settingsTable.setWidget(row++, 1, deliveryPanel);
		settingsTable.setWidget(row, 0, inputTypeLabel);
		settingsTable.setWidget(row++, 1, maxInputControls);
		settingsTable.setWidget(row, 0, freeInboundLabel);
		settingsTable.setWidget(row++, 1, inboundButtons);
		settingsTable.setWidget(row, 0, backupsLabel);
		settingsTable.setWidget(row++, 1, backupsBox);
		settingsTable.setWidget(row, 0, forwardLabel);
		settingsTable.setWidget(row++, 1, forwardAllowed);
		settingsTable.setWidget(row, 0, emailLabel);
		settingsTable.setWidget(row++, 1, emailPanel);
		settingsTable.setWidget(row, 0, senderLabel);
		settingsTable.setWidget(row++, 1, senderPanel);
		settingsTable.setWidget(row, 0, publishersLabel);
		settingsTable.setWidget(row++, 1, pubsPanel);
		settingsTable.setWidget(row, 0, greetingLabel);
		settingsTable.setWidget(row++, 1, greetingMessage);
		
		HorizontalPanel controls = new HorizontalPanel();
		controls.setSpacing(10);
		controls.setWidth("100%");
		if (Messages.get().getModerator().getMaxGroups() != User.DISABLE_GROUP_ADD_REMOVE)
			controls.add(deleteButton);
		HorizontalPanel innercontrols = new HorizontalPanel();
		innercontrols.setSpacing(5);
		innercontrols.add(cancelButton);
		innercontrols.add(saveButton);
		controls.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_RIGHT);
		controls.add(innercontrols);
		
		settingsPanel.add(settingsTable);		
		settingsPanel.add(controls);
		
		/**************************************************
		 * 
		 *  Init the Widget
		 *  
		 *************************************************/
		groupid = new Hidden("groupid");
		groupid.setName("groupid");
		
		outer.add(tabPanel);
		//outer.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_RIGHT);
		//outer.add(controls);		
		outer.add(groupid);
		outer.add(memberStatus);
		outer.add(membersToUpdate);
		
		manageGroupsForm.setWidget(outer);
		
		initWidget(manageGroupsForm);
	}
	
	private void initTableColums(final SelectionModel<Membership> selectionModel)
	{
		// Add a checkbox column for bulk actions.
    Column<Membership, Boolean> checkColumn =
      new Column<Membership, Boolean>(new CheckboxCell(true, false)) {
        public Boolean getValue(Membership object) {
          // Get the value from the selection model.
          return selectionModel.isSelected(object);
        }
      };
      
    CheckboxCell headerCheckbox = new CheckboxCell(true, false);
    Header<Boolean> selectPageHeader = new Header<Boolean>(headerCheckbox) {
      @Override
      public Boolean getValue() {
        for (Membership item : memberTable.getVisibleItems()) {
          if (!memberTable.getSelectionModel().isSelected(item)) {
            return false;
          }
        }
        return memberTable.getVisibleItems().size() > 0;
      }
    };
    selectPageHeader.setUpdater(new ValueUpdater<Boolean>() {
      @Override
      public void update(Boolean value) {
        for (Membership item : memberTable.getVisibleItems()) {
          memberTable.getSelectionModel().setSelected(item, value);
        }
      }
    });
    
      
    memberTable.addColumn(checkColumn, selectPageHeader);
    memberTable.setColumnWidth(checkColumn, 40, Unit.PX);
    
    final Column<Membership, String> nameColumn = new Column<Membership, String>(new EditTextCell()) {
      public String getValue(Membership object) {
        // Return the name as the value of this column.
        String name = object.getMemberName();
      	if ("null".equals(name))
      		return "";
      	else
      		return name; 
      }
    };
    nameColumn.setSortable(true);
    
    memberTable.addColumn(nameColumn, "Name");
    nameColumn.setFieldUpdater(new FieldUpdater<Membership, String>() {
			public void update(int index, Membership object, String value) {
				if (!"".equals(value))
				{
					// check if name changed
		    	if (!object.getUser().getName().equals(value) && !value.equals(""))
		    	{
		    		String data = "name=" + value;
		        JSONRequest.doPost(AoAPI.UPDATE_MEMBER + object.getId() + "/", data);
		    	}
				}
				else
					// added this based on advice on how to restore the value of a cell in case of validation error
					// solution from https://groups.google.com/d/msg/google-web-toolkit/sPRy0lqACsc/UJH-jvBNAcIJ
					((EditTextCell)nameColumn.getCell()).clearViewData(memberTable.getKeyProvider().getKey(object));
			}
    });
    memberTable.setColumnWidth(nameColumn, 50, Unit.PCT);
    
    Column<Membership, String> numberColumn = new Column<Membership, String>(new TextCell()) {
      public String getValue(Membership object) {
        // Return the name as the value of this column.
        return object.getUser().getNumber();
      }
    };
    numberColumn.setSortable(true);
    
    memberTable.addColumn(numberColumn, "Number");
    memberTable.setColumnWidth(numberColumn, 30, Unit.PCT);
    
    Column<Membership, String> statusColumn = new Column<Membership, String>(new TextCell()) {

			public String getValue(Membership object) {
					return object.getStatus().getTxtValue();
			}
    	
    };
    memberTable.addColumn(statusColumn, "Status");

	}
	
	private void initJoinTableColums(final SelectionModel<Membership> selectionModel)
	{
		// Add a checkbox column for bulk actions.
    Column<Membership, Boolean> checkColumn =
      new Column<Membership, Boolean>(new CheckboxCell(true, false)) {
        public Boolean getValue(Membership object) {
          // Get the value from the selection model.
          return selectionModel.isSelected(object);
        }
      };
      
    CheckboxCell headerCheckbox = new CheckboxCell(true, false);
    Header<Boolean> selectPageHeader = new Header<Boolean>(headerCheckbox) {
      @Override
      public Boolean getValue() {
        for (Membership item : joinsTable.getVisibleItems()) {
          if (!joinsTable.getSelectionModel().isSelected(item)) {
            return false;
          }
        }
        return joinsTable.getVisibleItems().size() > 0;
      }
    };
    selectPageHeader.setUpdater(new ValueUpdater<Boolean>() {
      @Override
      public void update(Boolean value) {
        for (Membership item : joinsTable.getVisibleItems()) {
        	joinsTable.getSelectionModel().setSelected(item, value);
        }
      }
    });
      
    joinsTable.addColumn(checkColumn, selectPageHeader);
    joinsTable.setColumnWidth(checkColumn, 40, Unit.PX);
    
    Column<Membership, String> nameColumn = new Column<Membership, String>(new TextCell()) {
      public String getValue(Membership object) {
      	// Return the name as the value of this column.
        String name = object.getMemberName();
      	if ("null".equals(name))
      		return "";
      	else
      		return name;
      }
    };
    nameColumn.setSortable(true);
    
    joinsTable.addColumn(nameColumn, "Name");
    joinsTable.setColumnWidth(nameColumn, 60, Unit.PCT);
    
    Column<Membership, String> numberColumn = new Column<Membership, String>(new TextCell()) {
      public String getValue(Membership object) {
        // Return the name as the value of this column.
        return object.getUser().getNumber();
      }
    };
    numberColumn.setSortable(true);
    
    joinsTable.addColumn(numberColumn, "Number");
    joinsTable.setColumnWidth(numberColumn, 40, Unit.PCT);

	}
	
	private void initReportColumns()
	{
    Column<Broadcast, String> dateColumn = new Column<Broadcast, String>(new TextCell()) {
      public String getValue(Broadcast object) {
        // Return the name as the value of this column.
        return object.getDate();
      }
    };
    
    reportTable.addColumn(dateColumn, "Date");
    reportTable.setColumnWidth(dateColumn, 20, Unit.PCT);
    
    Column<Broadcast, String> attemptsColumn = new Column<Broadcast, String>(new TextCell()) {
      public String getValue(Broadcast object) {
        // Return the name as the value of this column.
        return object.getAttempts();
      }
    };
    
    reportTable.addColumn(attemptsColumn, "Attempts");
    reportTable.setColumnWidth(attemptsColumn, 20, Unit.PCT);
    
    Column<Broadcast, String> maturedColumn = new Column<Broadcast, String>(new TextCell()) {
      public String getValue(Broadcast object) {
        // Return the name as the value of this column.
        return object.getMatured();
      }
    };
    
    reportTable.addColumn(maturedColumn, "Pickups");
    reportTable.setColumnWidth(maturedColumn, 20, Unit.PCT);
    
    Column<Broadcast, String> costColumn = new Column<Broadcast, String>(new TextCell()) {
      public String getValue(Broadcast object) {
        // Return the name as the value of this column.
        return object.getCost();
      }
    };
    
    reportTable.addColumn(costColumn, "Credits");
    reportTable.setColumnWidth(costColumn, 20, Unit.PCT);
    
    Column<Broadcast, Broadcast> downloadColumn = new Column<Broadcast,Broadcast>(new ActionCell<Broadcast>("Download", new ActionCell.Delegate<Broadcast>() {

			public void execute(Broadcast bcast) {
				if (bcast.getReportLink() != null)
					Window.open(JSONRequest.BASE_URL+AoAPI.DOWNLOAD_BCAST_REPORT + bcast.getId(), "Download Report", "");
				else
				{
					ConfirmDialog notAvailable = new ConfirmDialog("Report is currently unavailable. Check back after the broadcast completes");
					notAvailable.show();
					notAvailable.center();
				}
			}
		})) {

			public Broadcast getValue(Broadcast object) {
				return object;
			}
    	
    };
    reportTable.addColumn(downloadColumn, "Details");
    reportTable.setColumnWidth(downloadColumn, 20, Unit.PCT);

	}
	
	private void loadMembers()
	{
		MembershipStatus statuses[] = {MembershipStatus.SUBSCRIBED, MembershipStatus.INVITED, MembershipStatus.UNSUBSCRIBED};
		loadMembers(statuses);
	}
	
	private void loadMembers(MembershipStatus statuses[])
	{	
		JSONRequest request = new JSONRequest();
		String params = "/?start="+membersStartIndex+"&length="+String.valueOf(memberTable.getPageSize())+"&status=";
		for (MembershipStatus s : statuses)
		{
			params += s.getCode() + " ";
		}
		ColumnSortList sortList = memberTable.getColumnSortList();
    if (sortList != null && sortList.size() > 0)
    {
    	params += "&orderby=";
    	ColumnSortInfo sortInfo = sortList.get(0);
    	Column <Membership, ?> sortColumn = (Column <Membership, ?>) 
	                                          sortInfo.getColumn();
	    int columnIndex = memberTable.getColumnIndex(sortColumn);
	    boolean isAscending = sortInfo.isAscending();
	    if (columnIndex == 1)
	    	// Name
	    	params += isAscending ? "membername" : "-membername";
	    else if (columnIndex == 2)
	    	// Number
	    	params += isAscending ? "user__number" : "-user__number";
    }
		
		request.doFetchURL(AoAPI.MEMBERS + group.getId() + params, new MemberRequestor());
	}
	
	private void loadJoinRequests()
	{	
		JSONRequest request = new JSONRequest();
		String params = "/?start="+membersStartIndex+"&length="+String.valueOf(joinsTable.getPageSize())+"&status="+MembershipStatus.REQUESTED.getCode();
		ColumnSortList sortList = joinsTable.getColumnSortList();
    if (sortList != null && sortList.size() > 0)
    {
    	params += "&orderby=";
    	ColumnSortInfo sortInfo = sortList.get(0);
    	Column <Membership, ?> sortColumn = (Column <Membership, ?>) 
	                                          sortInfo.getColumn();
	    int columnIndex = joinsTable.getColumnIndex(sortColumn);
	    boolean isAscending = sortInfo.isAscending();
	    if (columnIndex == 1)
	    	// Name
	    	params += isAscending ? "membername,-last_updated" : "-membername,-last_updated";
	    else if (columnIndex == 2)
	    	// Number
	    	params += isAscending ? "user__number,-last_updated" : "-user__number,-last_updated";
    }
    else
    	params += "&orderby=-last_updated";
    
		request.doFetchURL(AoAPI.MEMBERS + group.getId() + params, new MemberRequestor());
		
	}
	
	private void loadSettings()
	{	
		groupNumber.setText("0"+line.getNumber());
		groupNameText.setValue(group.getName());
		String lang = line.getLanguage();
		for (int i=0; i<languageBox.getItemCount(); i++)
		{
			if (languageBox.getValue(i).equals(lang))
			{
				languageBox.setSelectedIndex(i);
				break;
			}
		}
		ForumStatus status = group.getStatus();
		for (int i=0; i<deliveryBox.getItemCount(); i++)
		{
			if (Integer.valueOf(deliveryBox.getValue(i)) == status.getCode())
			{
				deliveryBox.setSelectedIndex(i);
				break;
			}
		}
		
		/*
		 *  This works as long as there are only two input types and
		 *  their order in the box matches their boolean value.
		 *  
		 *  Lot of shortcuts to make the code faster (but less readable).
		 */
		int inputType = group.responsesAllowed() ? 1 : 0;
		inputBox.setSelectedIndex(inputType);
		
		if (inputType == 0)
		{
			// touchtone
			maxInputLabel.setVisible(true);
			int maxInputLength = group.getMaxInputLength();
			maxInputLengthBox.setItemSelected(maxInputLength-1, true);
			maxInputLengthBox.setVisible(true);
			
		}
		else
		{
			// voice
			maxInputLabel.setVisible(false);
			maxInputLengthBox.setVisible(false);
		}
		
		if (line.callback())
		{
			if (line.open())
				inboundAll.setValue(true);
			else
				inboundMemsOnly.setValue(true);
		}
		else
			inboundOff.setValue(true);
		
		String backups = group.getBackups();
		if ("null".equals(backups))
			backupsBox.setSelectedIndex(0);
		else
			backupsBox.setSelectedIndex(Integer.valueOf(backups));
		
		forwardAllowed.setValue(group.forwarding());
		
		String email = Messages.get().getModerator().getEmail();
		emailText.setValue(email);
		
		String sendername = group.getSenderName();
		if (!"null".equals(sendername))
			senderText.setValue(sendername);
		
		List<User> responders = group.getResponders();
		String pubsStr = "";
		for (User u : responders)
		{
			pubsStr += u.getNumber() + "\n";
		}
		publishersArea.setValue(pubsStr);
		
		greetingMessage.clearCell(0, 0);
		if (!"".equals(group.getNameFile()) && !"null".equals(group.getNameFile()))
		{
			SoundWidget sound = new SoundWidget(group.getNameFile());
			greetingMessage.setHTML(0, 0, sound.getWidget().getHTML());
		}
		
		creditsLabel.setHTML("You can add up to <b>"+group.getAddMemberCredits()+"</b> more members to this group. Contact us to add more.");
		
	}
	
	public void loadReports(int start)
	{
		JSONRequest request = new JSONRequest();
		String params = "/?start=0&length="+String.valueOf(reportTable.getPageSize());
		request.doFetchURL(AoAPI.BROADCAST_REPORTS + group.getId() + params, new BcastReportRequestor());
	}
	
	private class UpdateMembersComplete implements SubmitCompleteHandler {
			private String confirm;
			
			public UpdateMembersComplete(String confirm)
			{
				this.confirm = confirm;
			}
			
			public void onSubmitComplete(SubmitCompleteEvent event) {
				ConfirmDialog sent = new ConfirmDialog(confirm);
				sent.center();
		  	
		  	submitComplete();
		  	tabPanel.selectTab(0);
		}
	}
	
	private class AddMembersComplete implements SubmitCompleteHandler {
		public void onSubmitComplete(SubmitCompleteEvent event) {
			List<JSOModel> models = JSONRequest.getModels(event.getResults());
			// check first model for validation error
			JSOModel first = models.get(0);
			if (first.get("model").equals("VALIDATION_ERROR"))
			{
				ConfirmDialog err = new ConfirmDialog(first.get("message"));
				err.center();
				submitComplete();
			}
			else
			{
				String added = "";
				String notAdded = "";
				
		  	List<Membership> members = new ArrayList<Membership>();
		  	Membership m;
		  	
		  	for (JSOModel model : models)
		  	{
		  		if (model.get("model").equals(AoAPI.MEMBER_METADATA))
		  		{
		  			String addMemberCredits = model.get("add_member_credits");
		  			creditsLabel.setHTML("You can add up to <b>"+addMemberCredits+"</b> more members to this group. Contact us to add more.");
		  			
		  			// comma-seperated lists
		  			added = model.get("added");
		  			notAdded = model.get("notadded");
		  		}
		  		else // Assume it's a Membership model
		  		{
		  			members.add(new Membership(model));
		  		}
		  	}
		  	
		  	AddMembersDialog details = new AddMembersDialog(added, notAdded);
				details.center();
		  	
		  	submitComplete();
		  	tabPanel.selectTab(0);
			}
		}
	}
		
	private class AddMembersDialog extends DialogBox {

	  public AddMembersDialog(String added, String notAdded) {
	  	//setWidth("500px");
	    // Use this opportunity to set the dialog's caption.
	    setText("Awaaz.De Administration");

	    // Create a VerticalPanel to contain the 'about' label and the 'OK' button.
	    VerticalPanel outer = new VerticalPanel();
	    outer.setWidth("100%");
	    outer.setSpacing(10);
	    
	    HTML confirm = new HTML("<b>Members added!</b>");
	    confirm.setStyleName("dialog-headerText");
	    outer.add(confirm);
	    
	    HTML addedTitle = new HTML("<b>Added:</b>");
	    addedTitle.setStyleName("dialog-headerText");
			outer.add(addedTitle);
			Label addedLbl = new Label(added, true);
	    addedLbl.setWordWrap(true);
	    addedLbl.setStyleName("dialog-NumsText");
	    outer.add(addedLbl);
	    
	    HTML notAddedTitle = new HTML("<b>Not Added (already joined or unsubscribed):</b>");
	    notAddedTitle.setStyleName("dialog-headerText");
			outer.add(notAddedTitle);
			Label notAddedLbl = new Label(notAdded, true);
			notAddedLbl.setWordWrap(true);
			notAddedLbl.setStyleName("dialog-NumsText");
	    outer.add(notAddedLbl);

	    // Create the 'OK' button, along with a handler that hides the dialog
	    // when the button is clicked.
	    outer.add(new Button("Close", new ClickHandler() {
	      public void onClick(ClickEvent event) {
	        hide();
	      }
	    }));

	    setWidget(outer);
	  }

	  @Override
	  public boolean onKeyDownPreview(char key, int modifiers) {
	    // Use the popup's key preview hooks to close the dialog when either
	    // enter or escape is pressed.
	    switch (key) {
	      case KeyCodes.KEY_ENTER:
	      case KeyCodes.KEY_ESCAPE:
	        hide();
	        break;
	    }

	    return true;
	  }
	}
	
	private class SettingsComplete implements SubmitCompleteHandler {
		
		public void onSubmitComplete(SubmitCompleteEvent event) {
			ConfirmDialog confirm;
			List<JSOModel> models = JSONRequest.getModels(event.getResults());
	
			JSOModel model = models.get(0);
			if (model.get("model").equals("VALIDATION_ERROR"))
			{
				String msg = model.get("message");
				confirm = new ConfirmDialog(msg);
				confirm.center();
				
				submitComplete();
				loadSettings();
			}
			else
			{
				confirm = new ConfirmDialog("Settings updated!");
				confirm.show();
				confirm.center();
				
		  	submitComplete();
		  	
		  	Line l;
		  	// Find and update the currently selected group
		  	for (JSOModel m : models)
		  	{
		  		l = new Line(m);
		  		if (line.getId().equals(l.getId()))
					{
		  			line = l;
		  			group = line.getForums().get(0);
					}
		  	}
		  	
		  	// update the forum widget that corresponds
		  	// to this group
			  Messages.get().reloadGroup(line, group);
		  	
		  	// May have updated the email address of the moderator, 
		  	// so reload her.
		  	JSONRequest request = new JSONRequest();
			  request.doFetchURL(AoAPI.MODERATOR, new ModeratorRequestor());
			}
		}
	}
	
 private class ModeratorRequestor implements JSONRequester {
	 
		public void dataReceived(List<JSOModel> models) 
		{
			// for e.g. superuser will not have an associated AO_admin record
			if (models.size() > 0)
			{
				User moderator = new User(models.get(0));
				Messages.get().setModerator(moderator);
			}
			// reset
			loadSettings();
		}
	 }
	
private class DeleteComplete implements SubmitCompleteHandler {
		
		public void onSubmitComplete(SubmitCompleteEvent event) {
			ConfirmDialog removed = new ConfirmDialog("Group removed!");
			removed.show();
			removed.center();
			List<JSOModel> models = JSONRequest.getModels(event.getResults());
			
	  	submitComplete();
	  	
	  	Messages.get().reloadGroups(models);
		}
	}
	
	public void reset(Line line, Forum group)
	{ 
		 this.group = group;
		 this.line = line;
		 manageGroupsForm.reset();
		 loadSettings();
		 groupid.setValue(group.getId());
		 
		 // select tab explicitly so that
		 // membertable loads properly
		 tabPanel.selectTab(0);
		
	 }

	private void setClickedButton()
	{
		saveButton.setEnabled(false);
		addMembersButton.setEnabled(false);
		cancelAddMembers.setEnabled(false);
		cancelButton.setEnabled(false);
		deleteButton.setEnabled(false);
	}
	
	private void submitComplete()
	{
		saveButton.setEnabled(true);
		addMembersButton.setEnabled(true);
		cancelAddMembers.setEnabled(true);
		cancelButton.setEnabled(true);
		deleteButton.setEnabled(true);
	}
	
	private void showMemberTable() {
		// hide add members panel
		addMembersPanel.setVisible(false);
		
		// show member table stuff
		memberControls.setVisible(true);
		statusFilterBox.setSelectedIndex(0);
		memberTable.setVisible(true);
		pager.setVisible(true);
		
		// This is invoked in the tab panel
		// select event for the members panel
		// on memberTable.setVisibleRangeAndClearData(memberTable.getVisibleRange(), true); 
		//loadMembers();
		
	}
	
	private void showAddMembersView() {
		tabPanel.selectTab(0);
		// hide member table stuff
		memberControls.setVisible(false);
		memberTable.setVisible(false);
		pager.setVisible(false);
		
		// reset add members stuff
		numbersArea.setValue("");
		namesArea.setValue("");
		namesPanel.setVisible(false);
		welcomeSMS.setValue(false);
		addMembersPanel.setVisible(true);
		
	}
	
	private class UpdateMemberClickHandler implements ClickHandler {
		DataGrid<Membership> table;
		String areYouSureText, confirmText;
		MembershipStatus status;
		
		public UpdateMemberClickHandler(DataGrid<Membership> table, String areYouSureText, MembershipStatus status, String confirmText)
		{
			this.table = table;
			this.areYouSureText = areYouSureText;
			this.status = status;
			this.confirmText = confirmText;
			
		}
		@Override
		public void onClick(ClickEvent event) {
			Set<Membership> selectedMems = ((MultiSelectionModel<Membership>)table.getSelectionModel()).getSelectedSet();
			if (selectedMems.size() == 0)
			{
				ConfirmDialog noneSelected = new ConfirmDialog("No members selected. Please check the boxes for rows you want to update.");
				noneSelected.show();
				noneSelected.center();
			}
			else
			{
				confirm = new AreYouSureDialog(areYouSureText);
				confirm.show();
				confirm.center();
				
				confirm.addCloseHandler(new CloseHandler<PopupPanel>() {
					public void onClose(CloseEvent<PopupPanel> event) {
						if (confirm.isConfirmed())
						{
							memberStatus.setValue(String.valueOf(status.getCode()));
							Set<Membership> selectedMems = ((MultiSelectionModel<Membership>)table.getSelectionModel()).getSelectedSet();
							String memberIds = "";
							for (Membership m : selectedMems)
							{
								memberIds += m.getId() + ",";
								// clear selected
								table.getSelectionModel().setSelected(m, false);
							}
							membersToUpdate.setValue(memberIds);
							
							if (submitHandler != null)
							{
								submitHandler.removeHandler();
								submitHandler = null;
							}
							submitHandler = manageGroupsForm.addSubmitCompleteHandler(new UpdateMembersComplete(confirmText));
							
			      	manageGroupsForm.setAction(JSONRequest.BASE_URL + AoAPI.UPDATE_MEMBER_STATUS);
			      	manageGroupsForm.setEncoding(FormPanel.ENCODING_URLENCODED);
			      	manageGroupsForm.submit();
						}
						
					}
				});
				
			}
			
		}
		
	}
	
	/**
	 * Code taken and slighly modified at 
	 * http://stackoverflow.com/a/12235786/199754
	 * 
	 * Solution needed to page the last page properly, AND
	 * not have unending next page.
	 * 
	 * @author neil
	 *
	 */
	public class MembersPager extends SimplePager {

    public MembersPager() {
        this.setRangeLimited(true);
    }

    public MembersPager(TextLocation location, Resources resources, boolean showFastForwardButton, int fastForwardRows, boolean showLastPageButton) {
        super(location, resources, showFastForwardButton, fastForwardRows, showLastPageButton);
        this.setRangeLimited(true);
    }

		public void setPageStart(int index) {
	
	    if (this.getDisplay() != null) {
	      Range range = getDisplay().getVisibleRange();
	      int pageSize = range.getLength();
	      if (!isRangeLimited() && getDisplay().isRowCountExact()) {
	        index = Math.min(index, getDisplay().getRowCount() - pageSize);
	      }
	      index = Math.max(0, index);
	      if (index != range.getStart()) {
	        getDisplay().setVisibleRange(index, pageSize);
	      }
	    }  
	  }
	}
	
	private AsyncDataProvider<Membership> membersDataProvider = new AsyncDataProvider<Membership>() {

		protected void onRangeChanged(HasData<Membership> display) {
			if (group != null)
			{
				membersStartIndex = display.getVisibleRange().getStart();
	      int selectedTabIndex = tabPanel.getTabBar().getSelectedTab(); 
	      if (selectedTabIndex == 0)
	      {
	      	String code = statusFilterBox.getValue(statusFilterBox.getSelectedIndex());
	      	if (!code.equals("-1"))
					{
						MembershipStatus status[] = {MembershipStatus.getStatus(Integer.valueOf(code))};
						loadMembers(status);
					}
					else
						loadMembers();

	      }
	      else if (selectedTabIndex == 1)
	      {
	      	loadJoinRequests();
	      }
			}
			
		}
	};
	
	private class MemberRequestor implements JSONRequester {
		 
		public void dataReceived(List<JSOModel> models) {
			List<Membership> members = new ArrayList<Membership>();
			
			for (JSOModel model : models)
	  	{
				if (Membership.MODEL_TYPE.equals(model.get("model")))
				{
					members.add(new Membership(model));
				}
				else if (model.get("model").equals(AoAPI.MEMBER_METADATA))
	  		{
					int rowcount = Integer.valueOf(model.get("total"));
					membersDataProvider.updateRowCount(rowcount, true);
					
					int joinrequests = Integer.valueOf(model.get("requests"));
					if (joinrequests > 0)
					{
						tabPanel.getTabBar().setTabText(1, "Join Requests ("+joinrequests+")");
					}
					else
					{
						tabPanel.getTabBar().setTabText(1, "Join Requests");
					}
				}
	  	}
			
			membersDataProvider.updateRowData(membersStartIndex, members);
			Messages.get().displayManageGroupsInterface(group);
			
		}
	 }
	
	private AsyncDataProvider<Broadcast> reportsDataProvider = new AsyncDataProvider<Broadcast>() {

		protected void onRangeChanged(HasData<Broadcast> display) {
			if (group != null)
			{
				reportStartIndex = display.getVisibleRange().getStart();
	      int length = display.getVisibleRange().getLength();
	      String params = "/?start="+reportStartIndex+"&length="+length;
	      JSONRequest request = new JSONRequest();
	      request.doFetchURL(AoAPI.BROADCAST_REPORTS + group.getId() + params, new BcastReportRequestor());
			}
			
		}
	};
	
	private class BcastReportRequestor implements JSONRequester {
		 
		public void dataReceived(List<JSOModel> models) {
			List<Broadcast> bcasts = new ArrayList<Broadcast>();
			Broadcast b;
			
			for (JSOModel model : models)
	  	{
				if (Broadcast.MODEL_TYPE.equals(model.get("model")))
				{
					b = new Broadcast(model);
					bcasts.add(b);
				}
				else if (Forum.isGroupMetadata(model))
				{
					int rowcount = Integer.valueOf(model.get("totalsurveys"));
					reportsDataProvider.updateRowCount(rowcount, true);
					
				}
	  	}
			
			// default report dropdown
			DateTimeFormat dtf = DateTimeFormat.getFormat("MM");
		  String currentMonthStr = dtf.format(new Date());
		  int currentMonth = Integer.valueOf(currentMonthStr);
		  month.setSelectedIndex(currentMonth-1);
		    
			reportsDataProvider.updateRowData(reportStartIndex, bcasts);
			
		}
	 }

	/**
   * Information about a member.
   */
  public static class MemberInfo {
      
    private Membership membership;

    public MemberInfo(Membership membership) {
    	this.membership = membership;
    }

    /**
     * @return the status of the membership
     */
    public MembershipStatus getStatus() {
      return membership.getStatus();
    }

    /**
     * @return the unique ID of the member
     */
    public String getId() {
      return membership.getId();
    }

    /**
     * @return the contact's name
     */
    public String getName() {
    	String name = membership.getMemberName();
    	if ("null".equals(name))
    		return "";
    	else
    		return name; 
    }

    /**
     * @return the contact's number
     */
    public String getNumber() {
      return membership.getUser().getNumber();
    }
  }
  
	/**
	 * Information about a broadcast.
	 */
	private class Broadcast extends BaseModel {
		private static final String MODEL_TYPE = "BCAST_METADATA";
		
	  public Broadcast(JSOModel data) {
			super(data);
		}
	
	
	  public String getDate() {
	    return get("date").replace("T", " ");
	  }
	
	  public String getId() {
	  	return get("surveyid");
	  }
	
	  public String getAttempts() {
	  	return get("attempts"); 
	  }
	  
	  public String getMatured() {
	  	return get("matured"); 
	  }
	
	  public String getCost() {
	    return get("cost");
	  }
	  
	  public String getReportLink()
	  {
	  	String link = get("report");
	  	if ("0".equals(link))
	    	return null;
	    else
	    	return link;
	  }
	  
	}
	
}
