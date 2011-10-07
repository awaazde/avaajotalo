package org.otalo.ao.client;

import java.util.Date;
import java.util.List;

import org.otalo.ao.client.JSONRequest.AoAPI;
import org.otalo.ao.client.model.BaseModel;
import org.otalo.ao.client.model.Forum;
import org.otalo.ao.client.model.JSOModel;
import org.otalo.ao.client.model.Line;
import org.otalo.ao.client.model.Message.MessageStatus;
import org.otalo.ao.client.model.MessageForum;
import org.otalo.ao.client.model.Prompt;
import org.otalo.ao.client.model.Survey;
import org.otalo.ao.client.model.Tag;

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
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.DecoratedStackPanel;
import com.google.gwt.user.client.ui.FileUpload;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteEvent;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteHandler;
import com.google.gwt.user.client.ui.AbstractImagePrototype;
import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.HasVerticalAlignment;
import com.google.gwt.user.client.ui.Hidden;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.RadioButton;
import com.google.gwt.user.client.ui.TextArea;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.datepicker.client.DatePicker;

public class BroadcastInterface extends Composite {
	private FormPanel bcastForm;
	private DecoratedStackPanel stackPanel = new DecoratedStackPanel();
	private VerticalPanel outer, who, what, when;
	private HorizontalPanel controls = new HorizontalPanel();
	private Button sendButton, cancelButton;
	private TextBox sinceField, bcastDateField;
	private DatePicker since, bcastDate;
	private ListBox tags, lastNCallers, templates, from, till, duration, blockSize, interval;
	private Hidden messageforumid, lineid;
	private CheckBox numbers, usersByTag, usersByLog;
	private RadioButton now, date;
	//private FileUpload fileUpload;
	private MessageForum thread;
	
	public interface Images extends Fora.Images {
		ImageResource group();
		ImageResource messagesgroup();
		ImageResource calendar();
	}
	
	public BroadcastInterface(Images images) {
		outer = new VerticalPanel();
		outer.setSize("100%","100%");
		bcastForm = new FormPanel();
		bcastForm.setWidget(outer);
		bcastForm.setMethod(FormPanel.METHOD_POST);
		bcastForm.setEncoding(FormPanel.ENCODING_MULTIPART);
		
		bcastForm.addSubmitCompleteHandler(new BroadcastComplete());
		
		stackPanel.setSize("100%", "100%");
		who = new VerticalPanel();
		who.setSize("100%", "100%");
		what = new VerticalPanel();
		what.setSize("100%", "100%");
		when = new VerticalPanel();
		when.setSize("100%", "100%");
		
		VerticalPanel whoPanel = new VerticalPanel();
		whoPanel.setSize("100%", "100%");
		numbers = new CheckBox("Numbers:");
		numbers.setName("bynumbers");
		usersByTag = new CheckBox("Users by Tag:");
		usersByTag.setName("bytag");
		usersByLog = new CheckBox("Last");
		usersByLog.setName("bylog");
		
		TextArea numbersArea = new TextArea();
		numbersArea.setName("numbersarea");
		numbersArea.setSize("350px", "100px");
		numbersArea.addFocusHandler(new FocusHandler() {
			public void onFocus(FocusEvent event) {
				numbers.setValue(true);
			}
		});
		tags = new ListBox(true);
		tags.setName("tag");
		tags.setVisibleItemCount(5);
		tags.addFocusHandler(new FocusHandler() {
			public void onFocus(FocusEvent event) {
				usersByTag.setValue(true);
			}
		});
		lastNCallers = new ListBox();
		lastNCallers.addItem("", "-1");
		lastNCallers.setName("lastncallers");
		lastNCallers.addFocusHandler(new FocusHandler() {
			public void onFocus(FocusEvent event) {
				usersByLog.setValue(true);
			}
		});
		for(int i=1; i < 6; i++)
		{
			lastNCallers.addItem(String.valueOf(i*100), String.valueOf(i*100));
		}
		lastNCallers.addItem("All", "ALL");
		
		Label usersSince = new Label("callers since");
		sinceField = new TextBox();
		sinceField.setName("since");
		since = new DatePicker();
		since.addValueChangeHandler(new ValueChangeHandler<Date>() {

			public void onValueChange(ValueChangeEvent<Date> event) {
				Date d = event.getValue();
				sinceField.setValue(DateTimeFormat.getFormat("MMM-dd-yyyy").format(d));
				since.setVisible(false);
				
			}
		});
		
		sinceField.addFocusHandler(new FocusHandler() {
			
			public void onFocus(FocusEvent event) {
				since.setVisible(true);		
				usersByLog.setValue(true);
			}
		});
		
		HorizontalPanel numbersPanel = new HorizontalPanel();
		numbersPanel.setSpacing(10);
		numbersPanel.add(numbers);
		numbersPanel.add(numbersArea);
		
		HorizontalPanel tagPanel = new HorizontalPanel();
		tagPanel.setSpacing(10);
		tagPanel.add(usersByTag);
		tagPanel.add(tags);
		
		HorizontalPanel logPanel = new HorizontalPanel();
		logPanel.setSpacing(10);
		logPanel.add(usersByLog);
		logPanel.add(lastNCallers);
		logPanel.add(usersSince);
		logPanel.add(sinceField);
		since.setVisible(false);
		logPanel.add(since);
		
		whoPanel.add(numbersPanel);
		whoPanel.add(tagPanel);
		whoPanel.add(logPanel);
		
		who.add(whoPanel);
		
		VerticalPanel whatPanel = new VerticalPanel();
		whatPanel.setSpacing(10);
		Label tempLbl = new Label("Template: ");
		CheckBox response = new CheckBox("Allow response");
		response.setName("response");
		
  	templates = new ListBox();
  	templates.setName("survey");
  	
  	HorizontalPanel surveyPanel = new HorizontalPanel();
  	surveyPanel.setSpacing(10);
  	surveyPanel.add(tempLbl);
  	surveyPanel.add(templates);
  	surveyPanel.add(response);
  	
  	what.add(surveyPanel);
  	
  	HorizontalPanel whenPanel = new HorizontalPanel();
  	whenPanel.setSpacing(10);
  	now = new RadioButton("when","Start now");
  	now.setFormValue("now");
  	now.addClickHandler(new ClickHandler() {
			public void onClick(ClickEvent event) {
				from.setEnabled(false);
				from.insertItem("NOW", "-1", 0);
				from.setSelectedIndex(0);
			}
		});
		date = new RadioButton("when","Date:");
		date.setFormValue("date");
		date.addClickHandler(new ClickHandler() {
			public void onClick(ClickEvent event) {
				from.setEnabled(true);
				from.clear();
				for(int i=1; i < 24; i++)
				{
					String time = String.valueOf(i) + ":00";
					from.addItem(time, String.valueOf(i));
				}
				from.setSelectedIndex(7);
			}
		});
		
		bcastDateField = new TextBox();
		bcastDateField.setName("bcastdate");
		bcastDate = new DatePicker();
		bcastDate.addValueChangeHandler(new ValueChangeHandler<Date>() {

			public void onValueChange(ValueChangeEvent<Date> event) {
				Date d = event.getValue();
				bcastDateField.setValue(DateTimeFormat.getFormat("MMM-dd-yyyy").format(d));
				bcastDate.setVisible(false);
				now.setValue(false);
				date.setValue(true);
				
			}
		});
		
		bcastDateField.addFocusHandler(new FocusHandler() {
			
			public void onFocus(FocusEvent event) {
				bcastDate.setVisible(true);
				now.setValue(false);
				date.setValue(true);
			}
		});
  	
		Label fromLbl = new Label("From");
		from = new ListBox();
		from.setName("fromtime");	
		Label tillLbl = new Label("till");
		till = new ListBox();
		till.setName("tilltime");
		for(int i=1; i < 24; i++)
		{
			String time = String.valueOf(i) + ":00";
			from.addItem(time, String.valueOf(i));
			till.addItem(time, String.valueOf(i));
		}
		
		Label makeLbl = new Label("Make");
		blockSize = new ListBox();
		blockSize.setName("blocksize");
		blockSize.addItem("5");
		blockSize.addItem("10");
		blockSize.addItem("15");
		blockSize.addItem("20");
		blockSize.addItem("25");
		blockSize.addItem("30");
		Label everyLbl = new Label("calls at a time, every");
		interval = new ListBox();
		interval.setName("interval");
		interval.addItem("2");
		interval.addItem("3");
		interval.addItem("4");
		interval.addItem("5");
		interval.addItem("6");
		interval.addItem("7");
		interval.addItem("8");
		interval.addItem("9");
		interval.addItem("10");
		Label minLbl = new Label("minutes");
		
		Label durationLbl = new Label("Duration (days):");
		duration = new ListBox();
		duration.setName("duration");
		for(int i=1; i < 7; i++)
		{
			duration.addItem(String.valueOf(i), String.valueOf(i));
		}
		HorizontalPanel fromTillPanel = new HorizontalPanel();
		fromTillPanel.setSpacing(10);
		fromTillPanel.add(fromLbl);
		fromTillPanel.add(from);
		fromTillPanel.add(tillLbl);
		fromTillPanel.add(till);
		
		HorizontalPanel blockPanel = new HorizontalPanel();
		blockPanel.setSpacing(10);
		blockPanel.add(makeLbl);
		blockPanel.add(blockSize);
		blockPanel.add(everyLbl);
		blockPanel.add(interval);
		blockPanel.add(minLbl);
		
		CheckBox backups = new CheckBox("Backup Calls");
		backups.setName("backups");
		
		HorizontalPanel nowPanel = new HorizontalPanel();
		nowPanel.setSpacing(10);
		nowPanel.add(now);
		
		HorizontalPanel datePanel = new HorizontalPanel();
		datePanel.setSpacing(10);
		datePanel.add(date);
		datePanel.add(bcastDateField);
		bcastDate.setVisible(false);
		datePanel.add(bcastDate);
		
		HorizontalPanel ftBlockPanel = new HorizontalPanel();
		ftBlockPanel.setWidth("65%");
		ftBlockPanel.add(fromTillPanel);
		ftBlockPanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_RIGHT);
		ftBlockPanel.add(blockPanel);
		
		HorizontalPanel durationPanel = new HorizontalPanel();
		durationPanel.setSpacing(10);
		durationPanel.add(durationLbl);
		durationPanel.add(duration);
		durationPanel.add(backups);
		
		when.add(nowPanel);
		when.add(datePanel);
		when.add(ftBlockPanel);
		when.add(durationPanel);
		
		stackPanel.add(who, createHeaderHTML(images.group(), "Recipients"), true);
		stackPanel.add(what, createHeaderHTML(images.messagesgroup(), "Template"), true);
		stackPanel.add(when, createHeaderHTML(images.calendar(), "Schedule"), true);
		
		controls = new HorizontalPanel();
		
		sendButton = new Button("Send", new ClickHandler() {
      public void onClick(ClickEvent event) {
      	setClickedButton();
    		templates.setEnabled(true);
      	bcastForm.setAction(JSONRequest.BASE_URL + AoAPI.BCAST_MESSAGE);
        bcastForm.submit();
      }
    });
		cancelButton = new Button("Cancel");
		cancelButton.addClickHandler(new ClickHandler(){
			public void onClick(ClickEvent event) {
				Messages.get().displayMessages(thread);
			}
			
		});
		
		controls.setSpacing(10);
		controls.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_RIGHT);
		controls.add(cancelButton);
		controls.add(sendButton);
		
		outer.add(stackPanel);
		outer.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_RIGHT);
		outer.add(controls);
		messageforumid = new Hidden("messageforumid");
		outer.add(messageforumid);
		lineid = new Hidden("lineid");
		lineid.setValue(Messages.get().getLine().getId());
		outer.add(lineid);
		
		initWidget(bcastForm);
	}
	
	public void loadTags()
	{	
		// Somewhat lazy way to not keep reloading
		// Assumes the admin can see only a single line at
		// a time (unless they are superuser), and assumes
		// line has at least one item associated with it
	  // (sh be at least 2 items counting blank space)
		if (tags.getItemCount() < 2)
		{
			JSONRequest request = new JSONRequest();		
			if (thread != null)
				request.doFetchURL(AoAPI.TAGS + thread.getForum().getId() + "/", new TagRequestor());
			else
				request.doFetchURL(AoAPI.TAGS_BY_LINE + Messages.get().getLine().getId() + "/", new TagRequestor());
		}
	}
	
	 private class TagRequestor implements JSONRequester {
		 
		public void dataReceived(List<JSOModel> models) {
			Tag t;
			
			for (JSOModel model : models)
		  	{
					t = new Tag(model);
					tags.addItem(t.getTag(), t.getId());
		  	}

		}
	 }
	 
	 public void broadcastThread(MessageForum thread)
	 { 
		 this.thread = thread;
		 JSONRequest request = new JSONRequest();
		 // in case it's a bcast without a thread
		 // to insert (holeless template)
		 if (thread != null)
		 {
			 messageforumid.setValue(thread.getId());
			 request.doFetchURL(AoAPI.FORWARD_THREAD + thread.getId() + "/", new BroadcastRequestor());
		 }
		 else
		 {
			 messageforumid.setValue(null);
			 request.doFetchURL(AoAPI.REGULAR_BCAST + Messages.get().getLine().getId() + "/", new BroadcastRequestor());
		 }
			 
		 
		 loadTags();
	 }
	 
	 private class BroadcastRequestor implements JSONRequester {
		 
			public void dataReceived(List<JSOModel> models) {
				Survey s;
				templates.clear();
				
				for (JSOModel model : models)
			  	{
						s = new Survey(model);
						templates.addItem(s.getName(), s.getId());
			  	}
				
				Messages.get().displayBroadcastPanel(thread);
				if (templates.getItemCount() == 1)
				{
					templates.setEnabled(false);
				}
				
			}
	 }
	 
	 private class BroadcastComplete implements SubmitCompleteHandler {
			
			public void onSubmitComplete(SubmitCompleteEvent event) {
				ConfirmDialog sent = new ConfirmDialog("Broadcast Scheduled!");
				sent.show();
				sent.center();
				
				sendComplete();
				Messages.get().loadBroadcasts(0);
				
				JSOModel model = JSONRequest.getModels(event.getResults()).get(0);
				/*
				 * Why not check for Prompt (bcast interface) here?
				 * Because in the bcast panel there may or may not be a prompt
				 * selected, so you don't know what to reload (we are not sending
				 * The selected prompt (if any) to the server on bcast post
				 * from New Broadcast link
				 */
				if (Forum.isForum(model))
				{
					// get the first forum for this moderator
					Forum f = new Forum(model);
					MessageStatus status;
					if (f.moderated())
						status = MessageStatus.PENDING;
					else
						status = MessageStatus.APPROVED;
					
					Messages.get().displayMessages(f, status, 0);
				}
				else if (MessageForum.isMessageForum(model))
				{
					MessageForum messageForum = new MessageForum(model);
					Messages.get().displayMessages(messageForum);
				}
		}
	 }
	 
	 public void reset(MessageForum mf)
	 {
		 bcastForm.reset();
		 // need to be explicit since these
		 // are activated indirectly (kinda weird)
		 numbers.setValue(false);
		 usersByTag.setValue(false);
		 usersByLog.setValue(false);
		 thread = mf;
		 // Select 7am-7pm by default
		 from.setEnabled(true);
		 from.clear();
		 for(int i=1; i < 24; i++)
			{
				String time = String.valueOf(i) + ":00";
				from.addItem(time, String.valueOf(i));
			}
		 from.setItemSelected(6, true);
		 till.setItemSelected(18, true);
		 blockSize.setSelectedIndex(1);
		 interval.setSelectedIndex(8);
		 lastNCallers.setItemSelected(3, true);
		 duration.setItemSelected(1,true);
		 
		 Date today = new Date();
		 since.setValue(today);
		 since.setVisible(false);
		 today.setDate(today.getDate() + 1);
		 bcastDateField.setValue(DateTimeFormat.getFormat("MMM-dd-yyyy").format(today));
		 bcastDate.setValue(today);
		 bcastDate.setVisible(false);

		 date.setValue(true);
		 
		 stackPanel.showStack(0);
	 }

	private void setClickedButton()
	{
		sendButton.setEnabled(false);
		cancelButton.setEnabled(false);
	}
		
	private void sendComplete()
	{
		sendButton.setEnabled(true);
		cancelButton.setEnabled(true);
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
