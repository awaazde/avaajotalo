package org.otalo.ao.client;

import java.awt.TextField;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;

import org.otalo.ao.client.JSONRequest.AoAPI;
import org.otalo.ao.client.model.Forum;
import org.otalo.ao.client.model.JSOModel;
import org.otalo.ao.client.model.Line;
import org.otalo.ao.client.model.Message.MessageStatus;
import org.otalo.ao.client.model.MessageForum;
import org.otalo.ao.client.model.Tag;
import org.otalo.ao.client.model.User;

import com.google.gwt.event.dom.client.ChangeEvent;
import com.google.gwt.event.dom.client.ChangeHandler;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.dom.client.FocusEvent;
import com.google.gwt.event.dom.client.FocusHandler;
import com.google.gwt.event.logical.shared.ValueChangeEvent;
import com.google.gwt.event.logical.shared.ValueChangeHandler;
import com.google.gwt.i18n.client.DateTimeFormat;
import com.google.gwt.resources.client.ImageResource;
import com.google.gwt.user.client.ui.AbstractImagePrototype;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.DecoratedStackPanel;
import com.google.gwt.user.client.ui.DecoratedTabPanel;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteEvent;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteHandler;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.Hidden;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.RadioButton;
import com.google.gwt.user.client.ui.TabLayoutPanel;
import com.google.gwt.user.client.ui.TextArea;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.datepicker.client.DatePicker;

public class ManageGroups extends Composite {
	private DecoratedTabPanel tabPanel = new DecoratedTabPanel();
	private Hidden groupid;
	private Button saveButton, cancelButton;
	private ListBox groupBox;
	
	private List<Forum> groups = new ArrayList<Forum>();
	
	public interface Images extends Fora.Images {
		ImageResource group();
	}
	
	public ManageGroups(Images images) {
		VerticalPanel outer = new VerticalPanel();
		outer.setSize("100%","100%");
		
		Label groupLabel = new Label("Group");
		groupBox = new ListBox();
		groupBox.addChangeHandler(new ChangeHandler() {
			
			public void onChange(ChangeEvent event) {
				// Get groupid
				groupid.setValue(groupBox.getValue(groupBox.getSelectedIndex()));
				Forum group = groups.get(groupBox.getSelectedIndex());
				loadMembers(group);
			}
		});
		HorizontalPanel groupPanel = new HorizontalPanel();
		groupPanel.setSpacing(10);
		groupPanel.add(groupLabel);
		groupPanel.add(groupBox);
		
 		HorizontalPanel memberPanel = new HorizontalPanel();
		memberPanel.setSize("100%", "100%");
		HorizontalPanel settingsPanel = new HorizontalPanel();
		settingsPanel.setSize("100%", "100%");
		
		tabPanel.setSize("100%", "100%");
		tabPanel.add(memberPanel, "Members");
		tabPanel.add(settingsPanel, "Settings");
		
		HorizontalPanel controls = new HorizontalPanel();
		
		saveButton = new Button("Send", new ClickHandler() {
      public void onClick(ClickEvent event) {
      	setClickedButton();
      }
    });
		cancelButton = new Button("Cancel");
		cancelButton.addClickHandler(new ClickHandler(){
			public void onClick(ClickEvent event) {
					MessageStatus status;
					Forum group = groups.get(groupBox.getSelectedIndex());
					if (group.moderated())
						status = MessageStatus.PENDING;
					else
						status = MessageStatus.APPROVED;
					
					Messages.get().displayMessages(group, status, 0);
			}
			
		});
		
		controls.setSpacing(10);
		controls.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_RIGHT);
		controls.add(cancelButton);
		controls.add(saveButton);
		
		Hidden groupid = new Hidden("groupid");
		
		outer.add(groupPanel);
		outer.add(tabPanel);
		outer.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_RIGHT);
		outer.add(controls);		
		outer.add(groupid);
		
		initWidget(outer);
		
		loadGroups();
	}
	
	public void loadGroups()
	{	
		JSONRequest request = new JSONRequest();
		request.doFetchURL(AoAPI.GROUP, new GroupRequester());
	}
	
	public void loadMembers(Forum group)
	{	
		JSONRequest request = new JSONRequest();
		request.doFetchURL(AoAPI.MEMBERS + group.getId() + "/", new GroupMembersRequestor());
	}
	
	public void loadSettings(Forum group)
	{	
		// TODO
	}
	
	private class GroupRequester implements JSONRequester {
		 
		public void dataReceived(List<JSOModel> models) {
			Forum g;
			
			groups.clear();
			for (JSOModel model : models)
		  {
					g = new Forum(model);
					groupBox.addItem(g.getName(), g.getId());
					groups.add(g);
		  }
			
		}
	 }
	
	private class GroupMembersRequestor implements JSONRequester {
		 
		public void dataReceived(List<JSOModel> models) {
			User u;
			
			for (JSOModel model : models)
		  	{
					//TODO
		  	}

		}
	 }
	 
	 public void reset()
	 { 
		 // load up the first group by default
		 if (groups.size() > 0)
		 {
			 Forum group = groups.get(0);
			 loadMembers(group);
			 loadSettings(group);
		 }
		 tabPanel.selectTab(0);
		
	 }

	private void setClickedButton()
	{
		saveButton.setEnabled(false);
		cancelButton.setEnabled(false);
	}
		
	
	private String createHeaderHTML(ImageResource resource,
			String caption) {
		AbstractImagePrototype imageProto = AbstractImagePrototype.create(resource);
		String captionHTML = "<table class='caption' cellpadding='0' cellspacing='0'>"
				+ "<tr><td class='lcaption'>"
				+ imageProto.getHTML()
				+ "</td><td class='rcaption'><b style='white-space:nowrap'>"
				+ caption + "</b></td></tr></table>";
		return captionHTML;
	}

}
