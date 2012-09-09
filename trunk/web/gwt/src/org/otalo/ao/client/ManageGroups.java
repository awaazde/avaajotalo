package org.otalo.ao.client;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Set;

import org.otalo.ao.client.JSONRequest.AoAPI;
import org.otalo.ao.client.MemberDatabase.MemberInfo;
import org.otalo.ao.client.model.Forum;
import org.otalo.ao.client.model.Forum.ForumStatus;
import org.otalo.ao.client.model.BaseModel;
import org.otalo.ao.client.model.JSOModel;
import org.otalo.ao.client.model.Line;
import org.otalo.ao.client.model.Membership;
import org.otalo.ao.client.model.Survey;
import org.otalo.ao.client.model.Membership.MembershipStatus;
import org.otalo.ao.client.model.User;

import com.google.gwt.cell.client.ActionCell;
import com.google.gwt.cell.client.ButtonCell;
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
import com.google.gwt.event.logical.shared.CloseEvent;
import com.google.gwt.event.logical.shared.CloseHandler;
import com.google.gwt.event.logical.shared.SelectionEvent;
import com.google.gwt.event.logical.shared.SelectionHandler;
import com.google.gwt.resources.client.ImageResource;
import com.google.gwt.user.cellview.client.Column;
import com.google.gwt.user.cellview.client.ColumnSortEvent.ListHandler;
import com.google.gwt.user.cellview.client.DataGrid;
import com.google.gwt.user.cellview.client.Header;
import com.google.gwt.user.cellview.client.SimplePager;
import com.google.gwt.user.cellview.client.SimplePager.TextLocation;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.DecoratedTabPanel;
import com.google.gwt.user.client.ui.FileUpload;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteEvent;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteHandler;
import com.google.gwt.user.client.ui.HasAlignment;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.Hidden;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.PopupPanel;
import com.google.gwt.user.client.ui.TextArea;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.view.client.AsyncDataProvider;
import com.google.gwt.view.client.DefaultSelectionEventManager;
import com.google.gwt.view.client.HasData;
import com.google.gwt.view.client.MultiSelectionModel;
import com.google.gwt.view.client.ProvidesKey;
import com.google.gwt.view.client.Range;
import com.google.gwt.view.client.RangeChangeEvent;
import com.google.gwt.view.client.SelectionModel;
import com.google.web.bindery.event.shared.HandlerRegistration;

public class ManageGroups extends Composite {
	private DecoratedTabPanel tabPanel = new DecoratedTabPanel();
	private Hidden groupid, memberStatus, membersToUpdate;
	private Button saveButton, cancelButton, inviteButton, deleteButton;
	private ListBox languageBox, deliveryBox, inputBox, statusFilterBox;
	private DataGrid<MemberInfo> memberTable, joinsTable;
	private DataGrid<Broadcast> reportTable;
	private FormPanel manageGroupsForm;
	private VerticalPanel invitePanel, namesPanel;
	private HorizontalPanel memberControls;
	private FlexTable greetingMessage;
	private SimplePager pager;
	private TextBox groupNameText, emailText, senderText;
	private HandlerRegistration submitHandler = null;
	private AreYouSureDialog confirm;
	private TextArea numbersArea, namesArea;
	private Label groupNumber;
	private int reportStartIndex = 0;
	
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
	        showMemberTable();
        }
        else if (tabId == 1)
        	MemberDatabase.get().displayJoinRequests();
        else if (tabId == 2)
        	loadReports(0);
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
		Button inviteMembers = new Button("Invite members");
		inviteMembers.addClickHandler(new ClickHandler() {
			
			public void onClick(ClickEvent event) {
				showInviteView();
			}
			
		});
		Label filterLabel = new Label("Filter By");
		statusFilterBox = new ListBox();
		statusFilterBox.addItem("", "-1");
		statusFilterBox.addItem(Membership.MembershipStatus.INVITED.getTxtValue(), String.valueOf(MembershipStatus.INVITED.getCode()));
		statusFilterBox.addItem(Membership.MembershipStatus.SUBSCRIBED.getTxtValue(), String.valueOf(MembershipStatus.SUBSCRIBED.getCode()));
		statusFilterBox.addItem(Membership.MembershipStatus.UNSUBSCRIBED.getTxtValue(), String.valueOf(MembershipStatus.UNSUBSCRIBED.getCode()));
		
		statusFilterBox.addChangeHandler(new ChangeHandler() {

			public void onChange(ChangeEvent event) {
				String code = statusFilterBox.getValue(statusFilterBox.getSelectedIndex());
				MembershipStatus status = null;
				if (!code.equals("-1"))
				{
					status = MembershipStatus.getStatus(Integer.valueOf(code));
				}
				MemberDatabase.get().filterBy(status);
			}
		});
		
		memberControls.add(removeMembers);
		memberControls.add(inviteMembers);
				
		memberControls.setHorizontalAlignment(HasAlignment.ALIGN_RIGHT);
		HorizontalPanel filterPanel = new HorizontalPanel();
		filterPanel.add(filterLabel);
		filterPanel.add(statusFilterBox);
		filterPanel.setSpacing(5);
		memberControls.add(filterPanel);
		
		// Member Grid
		memberTable = new DataGrid<MemberInfo>(MemberDatabase.MemberInfo.KEY_PROVIDER);
		memberTable.setSize("850px", "320px");
		//memberTable.setRowCount(50, false);
		memberTable.setPageSize(50);
		
		// Add a selection model so we can select cells.
    final MultiSelectionModel<MemberInfo> selectionModel = new MultiSelectionModel<MemberInfo>(MemberDatabase.MemberInfo.KEY_PROVIDER);
    memberTable.setSelectionModel(selectionModel, DefaultSelectionEventManager.<MemberInfo> createCheckboxManager());
    ListHandler<MemberInfo> sortHandler = new ListHandler<MemberInfo>(MemberDatabase.get().getDataProvider().getList());
    memberTable.addColumnSortHandler(sortHandler);
    
    // Create a Pager to control the table.
    SimplePager.Resources pagerResources = GWT.create(SimplePager.Resources.class);
    pager = new MembersPager(TextLocation.CENTER, pagerResources, false, 0, true);
    pager.setPageSize(50);
    pager.setDisplay(memberTable);
    //pager.setRangeLimited(false);

    // Initialize the columns.
    initTableColums(selectionModel, sortHandler);

    // Add the member table to the adapter in the database.
    MemberDatabase.get().addDataDisplay(memberTable);
    
    memberPanel.add(memberControls);
    memberPanel.add(memberTable);
    memberPanel.setHorizontalAlignment(HasAlignment.ALIGN_CENTER);
    memberPanel.add(pager);
    removeMembers.addClickHandler(new UpdateMemberClickHandler(memberTable, "Are you sure you want to remove selected members from your group?", MembershipStatus.DELETED, "Members removed!"));
    
    /**************************************************
		 * 
		 * Invitation Interface
		 *  
		 *************************************************/    
    Label numbersLabel = new Label("Enter 10-digit numbers, one per line. Pasting from a spreadsheet is OK.");
    numbersLabel.setWordWrap(true);
    Anchor addNamesLink = new Anchor("Add Names");
		addNamesLink.addClickHandler(new ClickHandler() {
			
			public void onClick(ClickEvent event) {
					namesPanel.setVisible(true);
			}
				
		});
    Label numbersHelp = new Label("Each person will receive an invitation SMS to your group and must accept before they can receive messages.");
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
		
    memberPanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_LEFT);
    invitePanel = new VerticalPanel();
    invitePanel.setSpacing(10);
    invitePanel.add(numbersPanel);
    invitePanel.add(namesPanel);
		
		inviteButton = new Button("Send invitation SMS", new ClickHandler() {
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
	      	submitHandler = manageGroupsForm.addSubmitCompleteHandler(new UpdateMembersComplete("Invitations Sent!"));
	      	manageGroupsForm.setAction(JSONRequest.BASE_URL + AoAPI.INVITE_MEMBERS);
	      	manageGroupsForm.setEncoding(FormPanel.ENCODING_URLENCODED);
	      	manageGroupsForm.submit();
				}
    	}
    });
		
		Button cancelInvite = new Button("Cancel");
		cancelInvite.addClickHandler(new ClickHandler(){
			public void onClick(ClickEvent event) {
					showMemberTable();
			}
			
		});
		
		HorizontalPanel inviteButtonsPanel = new HorizontalPanel();
		inviteButtonsPanel.setSpacing(10);
		inviteButtonsPanel.add(cancelInvite);
		inviteButtonsPanel.add(inviteButton);
		invitePanel.setHorizontalAlignment(HasAlignment.ALIGN_RIGHT);
		invitePanel.add(inviteButtonsPanel);
		invitePanel.setVisible(false);
		
		memberPanel.add(invitePanel);
		
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
		
		joinsTable = new DataGrid<MemberInfo>(MemberDatabase.MemberInfo.KEY_PROVIDER);
		joinsTable.setSize("850px", "360px");
		joinsTable.setRowCount(50, true);
		
    joinsTable.setSelectionModel(selectionModel, DefaultSelectionEventManager.<MemberInfo> createCheckboxManager());
    joinsTable.addColumnSortHandler(sortHandler);

    // Create a Pager to control the table.
    MembersPager joinsPager = new MembersPager(TextLocation.CENTER, pagerResources, false, 0, true);
    joinsPager.setDisplay(joinsTable);
    MemberDatabase.get().addDataDisplay(joinsTable);

    // Initialize the columns.
    initJoinTableColums(selectionModel, sortHandler);
    
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
		// top-level widgets
		HorizontalPanel reportsTopPanel = new HorizontalPanel();
		reportsTopPanel.setSpacing(10);
		Label balanceLabel = new Label("Current Balance:");
		String balance = Messages.get().getModerator().getBalance();
		if ("null".equals(balance))
			balance = "0";
		Label balanceAmount = new Label(balance);
		Button rechargeBtn = new Button("Recharge");
		rechargeBtn.addClickHandler(new ClickHandler() {
			
			public void onClick(ClickEvent event) {
				ConfirmDialog recharge = new ConfirmDialog("Online payment coming soon! For now, please send a cheque to Awaaz.De to recharge your balance. Contact info@awaaz.de for bank details.");
				recharge.show();
				recharge.center();
				
			}
		});
		
		reportsTopPanel.add(balanceLabel);
		reportsTopPanel.add(balanceAmount);
		reportsTopPanel.add(rechargeBtn);
				
		// Reports Grid
		reportTable = new DataGrid<Broadcast>();
		reportTable.setSize("850px", "320px");
		
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
    
    reportsPanel.add(reportsTopPanel);
    reportsPanel.add(reportTable);
    reportsPanel.setHorizontalAlignment(HasAlignment.ALIGN_CENTER);
    reportsPanel.add(reportspager);
    
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
    languageBox.addItem("English", "eng");
    
    Label deliveryLabel = new Label("Delivery Type");
    deliveryBox = new ListBox();
    deliveryBox.setName("deliverytype");
    // hard-coding for now; stay consistent with forms.py:createacctform
    deliveryBox.addItem("Call + SMS", String.valueOf(Forum.ForumStatus.BCAST_CALL_SMS.getCode()));
    deliveryBox.addItem("SMS Only", String.valueOf(Forum.ForumStatus.BCAST_SMS.getCode()));
    
    Label inputTypeLabel = new Label("Response Type");
    inputBox = new ListBox();
    inputBox.setName("inputtype");
    // hard-coding for now; stay consistent with forms.py:createacctform
    inputBox.addItem("Touchtone", "0");
    inputBox.addItem("Voice", "1");
    
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
		settingsTable.setWidget(row++, 1, deliveryBox);
		settingsTable.setWidget(row, 0, inputTypeLabel);
		settingsTable.setWidget(row++, 1, inputBox);
		settingsTable.setWidget(row, 0, emailLabel);
		settingsTable.setWidget(row++, 1, emailPanel);
		settingsTable.setWidget(row, 0, senderLabel);
		settingsTable.setWidget(row++, 1, senderPanel);
		settingsTable.setWidget(row, 0, greetingLabel);
		settingsTable.setWidget(row++, 1, greetingMessage);
		
		HorizontalPanel controls = new HorizontalPanel();
		controls.setSpacing(10);
		controls.setWidth("100%");
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
	
	private void initTableColums(final SelectionModel<MemberInfo> selectionModel, ListHandler<MemberInfo> sortHandler)
	{
		// Add a checkbox column for bulk actions.
    Column<MemberInfo, Boolean> checkColumn =
      new Column<MemberInfo, Boolean>(new CheckboxCell(true, false)) {
        public Boolean getValue(MemberInfo object) {
          // Get the value from the selection model.
          return selectionModel.isSelected(object);
        }
      };
      
    CheckboxCell headerCheckbox = new CheckboxCell(true, false);
    Header<Boolean> selectPageHeader = new Header<Boolean>(headerCheckbox) {
      @Override
      public Boolean getValue() {
        for (MemberInfo item : memberTable.getVisibleItems()) {
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
        for (MemberInfo item : memberTable.getVisibleItems()) {
          memberTable.getSelectionModel().setSelected(item, value);
        }
      }
    });
    
      
    memberTable.addColumn(checkColumn, selectPageHeader);
    memberTable.setColumnWidth(checkColumn, 40, Unit.PX);
    
    final Column<MemberInfo, String> nameColumn = new Column<MemberInfo, String>(new EditTextCell()) {
      public String getValue(MemberInfo object) {
        // Return the name as the value of this column.
        return object.getName();
      }
    };
    nameColumn.setSortable(true);
    sortHandler.setComparator(nameColumn, new Comparator<MemberInfo>() {
			public int compare(MemberInfo m1, MemberInfo m2) {
				return m1.getName().compareTo(m2.getName());
			}
    });
    memberTable.addColumn(nameColumn, "Name");
    nameColumn.setFieldUpdater(new FieldUpdater<MemberInfo, String>() {
			public void update(int index, MemberInfo object, String value) {
				if (!"".equals(value))
					object.setName(value);
				else
					// added this based on advice on how to restore the value of a cell in case of validation error
					// solution from https://groups.google.com/d/msg/google-web-toolkit/sPRy0lqACsc/UJH-jvBNAcIJ
					((EditTextCell)nameColumn.getCell()).clearViewData(memberTable.getKeyProvider().getKey(object));
        MemberDatabase.get().refreshDisplays();
			}
    });
    memberTable.setColumnWidth(nameColumn, 50, Unit.PCT);
    
    Column<MemberInfo, String> numberColumn = new Column<MemberInfo, String>(new TextCell()) {
      public String getValue(MemberInfo object) {
        // Return the name as the value of this column.
        return object.getNumber();
      }
    };
    memberTable.addColumn(numberColumn, "Number");
    memberTable.setColumnWidth(numberColumn, 30, Unit.PCT);
    
    Column<MemberInfo, String> statusColumn = new Column<MemberInfo, String>(new TextCell()) {

			public String getValue(MemberInfo object) {
					return object.getStatus().getTxtValue();
			}
    	
    };
    statusColumn.setSortable(true);
    sortHandler.setComparator(statusColumn, new Comparator<MemberInfo>() {
			public int compare(MemberInfo m1, MemberInfo m2) {
				return m1.getStatus().getTxtValue().compareTo(m2.getStatus().getTxtValue());
			}
    });
    memberTable.addColumn(statusColumn, "Status");

	}
	
	private void initJoinTableColums(final SelectionModel<MemberInfo> selectionModel, ListHandler<MemberInfo> sortHandler)
	{
		// Add a checkbox column for bulk actions.
    Column<MemberInfo, Boolean> checkColumn =
      new Column<MemberInfo, Boolean>(new CheckboxCell(true, false)) {
        public Boolean getValue(MemberInfo object) {
          // Get the value from the selection model.
          return selectionModel.isSelected(object);
        }
      };
      
    CheckboxCell headerCheckbox = new CheckboxCell(true, false);
    Header<Boolean> selectPageHeader = new Header<Boolean>(headerCheckbox) {
      @Override
      public Boolean getValue() {
        for (MemberInfo item : joinsTable.getVisibleItems()) {
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
        for (MemberInfo item : joinsTable.getVisibleItems()) {
        	joinsTable.getSelectionModel().setSelected(item, value);
        }
      }
    });
      
    joinsTable.addColumn(checkColumn, selectPageHeader);
    joinsTable.setColumnWidth(checkColumn, 40, Unit.PX);
    
    Column<MemberInfo, String> nameColumn = new Column<MemberInfo, String>(new TextCell()) {
      public String getValue(MemberInfo object) {
        // Return the name as the value of this column.
        return object.getName();
      }
    };
    nameColumn.setSortable(true);
    sortHandler.setComparator(nameColumn, new Comparator<MemberInfo>() {
			public int compare(MemberInfo m1, MemberInfo m2) {
				return m1.getName().compareTo(m2.getName());
			}
    });
    joinsTable.addColumn(nameColumn, "Name");
    joinsTable.setColumnWidth(nameColumn, 60, Unit.PCT);
    
    Column<MemberInfo, String> numberColumn = new Column<MemberInfo, String>(new TextCell()) {
      public String getValue(MemberInfo object) {
        // Return the name as the value of this column.
        return object.getNumber();
      }
    };
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
    
    reportTable.addColumn(costColumn, "Cost (INR)");
    reportTable.setColumnWidth(costColumn, 20, Unit.PCT);
    
    Column<Broadcast, Broadcast> downloadColumn = new Column<Broadcast,Broadcast>(new ActionCell<Broadcast>("Download", new ActionCell.Delegate<Broadcast>() {

			public void execute(Broadcast bcast) {
				if (bcast.getReportLink() != null)
					Window.open(AoAPI.DOWNLOAD_BCAST_REPORT + bcast.getId(), "Download Report", "");
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
		JSONRequest request = new JSONRequest();
		request.doFetchURL(AoAPI.MEMBERS + group.getId() + "/", new GroupMembersRequestor());
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
		
		String email = Messages.get().getModerator().getEmail();
		emailText.setValue(email);
		
		String sendername = group.getSenderName();
		if (!"null".equals(sendername))
			senderText.setValue(sendername);
		
		greetingMessage.clearCell(0, 0);
		if (!"".equals(group.getNameFile()) && !"null".equals(group.getNameFile()))
		{
			SoundWidget sound = new SoundWidget(group.getNameFile());
			greetingMessage.setHTML(0, 0, sound.getWidget().getHTML());
		}
		
	}
	
	public void loadReports(int start)
	{
		JSONRequest request = new JSONRequest();
		String params = "/?start=0&length="+String.valueOf(reportTable.getPageSize());
		request.doFetchURL(AoAPI.BROADCAST_REPORTS + group.getId() + params, new BcastReportRequestor());
	}
	
	private class GroupMembersRequestor implements JSONRequester {
		 
		public void dataReceived(List<JSOModel> models) {
			List<Membership> members = new ArrayList<Membership>();
			
			for (JSOModel model : models)
		  	{
					members.add(new Membership(model));
		  	}
			
			MemberDatabase.get().addMembers(members);
			/*
			 * Need to call displayMembers explicitly here for reset
			 * since the call from reset on tab change will get triggered
			 * before this data retuns. So yes it's an extra call to display,
			 * but that should be cheap for a datagrid
			 *
			 * Note we call displayMembers since loading of new members will take
			 * us to that tab by default
			 */
			MemberDatabase.get().displayMembers();
			
			/*
			 * Now that members are loaded, pull the curtain on the interface
			 */
			Messages.get().displayManageGroupsInterface(group);
		}
	 }
	
	private class UpdateMembersComplete implements SubmitCompleteHandler {
			private String confirm;
			
			public UpdateMembersComplete(String confirm)
			{
				this.confirm = confirm;
			}
			public void onSubmitComplete(SubmitCompleteEvent event) {
				ConfirmDialog sent = new ConfirmDialog(confirm);
				sent.show();
				sent.center();
				
				List<JSOModel> models = JSONRequest.getModels(event.getResults());
		  	List<Membership> members = new ArrayList<Membership>();
		  	
		  	for (JSOModel model : models)
		  	{
		  		members.add(new Membership(model));
		  	}
		  	
		  	MemberDatabase.get().addMembers(members);
		  	MemberDatabase.get().refreshDisplays();
		  	submitComplete();
		  	showMemberTable();
		}
	}
	
	private class SettingsComplete implements SubmitCompleteHandler {
		
		public void onSubmitComplete(SubmitCompleteEvent event) {
			ConfirmDialog updated = new ConfirmDialog("Settings updated!");
			updated.show();
			updated.center();
			List<JSOModel> models = JSONRequest.getModels(event.getResults());
			
	  	submitComplete();
	  	
	  	Line l;
	  	String oldGroupName = group.getName();
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
		 loadMembers();
		 loadSettings();
		 groupid.setValue(group.getId());

		 // select tab explicitly so that
		 // membertable loads properly
		 tabPanel.selectTab(0);
		
	 }

	private void setClickedButton()
	{
		saveButton.setEnabled(false);
		inviteButton.setEnabled(false);
		cancelButton.setEnabled(false);
		deleteButton.setEnabled(false);
	}
	
	private void submitComplete()
	{
		saveButton.setEnabled(true);
		inviteButton.setEnabled(true);
		cancelButton.setEnabled(true);
		deleteButton.setEnabled(true);
	}
	
	private void showMemberTable() {
		// hide invite panel
		invitePanel.setVisible(false);
		
		// show member table stuff
		memberControls.setVisible(true);
		memberTable.setVisible(true);
		pager.setVisible(true);
		
		MemberDatabase.get().displayMembers();
		
	}
	
	private void showInviteView() {
		tabPanel.selectTab(0);
		// hide member table stuff
		memberControls.setVisible(false);
		memberTable.setVisible(false);
		pager.setVisible(false);
		
		// reset invitation stuff
		numbersArea.setValue("");
		namesArea.setValue("");
		namesPanel.setVisible(false);
		invitePanel.setVisible(true);
		
	}
	
	private class UpdateMemberClickHandler implements ClickHandler {
		DataGrid<MemberInfo> table;
		String areYouSureText, confirmText;
		MembershipStatus status;
		
		public UpdateMemberClickHandler(DataGrid<MemberInfo> table, String areYouSureText, MembershipStatus status, String confirmText)
		{
			this.table = table;
			this.areYouSureText = areYouSureText;
			this.status = status;
			this.confirmText = confirmText;
			
		}
		@Override
		public void onClick(ClickEvent event) {
			Set<MemberInfo> selectedMems = ((MultiSelectionModel<MemberInfo>)table.getSelectionModel()).getSelectedSet();
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
							Set<MemberInfo> selectedMems = ((MultiSelectionModel<MemberInfo>)table.getSelectionModel()).getSelectedSet();
							String memberIds = "";
							for (MemberInfo m : selectedMems)
							{
								memberIds += m.getId() + ",";
							}
							membersToUpdate.setValue(memberIds);
							
							// before submitting, clear any selected cells
							// (rejected members won't get cleared when server returns)
							MemberDatabase.get().refreshDisplays();
							
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
			
			reportsDataProvider.updateRowData(reportStartIndex, bcasts);
			
		}
	 }

	/**
	 * Information about a member.
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
