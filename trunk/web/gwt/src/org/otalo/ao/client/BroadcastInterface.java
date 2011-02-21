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
	private ListBox tags, lastNCallers, surveys, from, till, duration;
	private Hidden lineid, messageforumid;
	private RadioButton numbers, usersByTag, usersByLog, file, sms, survey, now, date;
	//private FileUpload fileUpload;
	private BaseModel backObj;
	
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
		numbers = new RadioButton("who","Numbers:");
		numbers.setFormValue("numbers");
		usersByTag = new RadioButton("who","Users by Tag:");
		usersByTag.setFormValue("tag");
		usersByLog = new RadioButton("who","Last");
		usersByLog.setFormValue("log");
		
		TextArea numbersArea = new TextArea();
		numbersArea.setName("numbersarea");
		numbersArea.setSize("350px", "100px");
		numbersArea.addFocusHandler(new FocusHandler() {
			public void onFocus(FocusEvent event) {
				numbers.setValue(true);
				usersByTag.setValue(false);
				usersByLog.setValue(false);
			}
		});
		tags = new ListBox(true);
		tags.setName("tag");
		tags.setVisibleItemCount(5);
		tags.addFocusHandler(new FocusHandler() {
			public void onFocus(FocusEvent event) {
				numbers.setValue(false);
				usersByTag.setValue(true);
				usersByLog.setValue(false);
			}
		});
		lastNCallers = new ListBox();
		lastNCallers.addItem("", "-1");
		lastNCallers.setName("lastncallers");
		lastNCallers.addFocusHandler(new FocusHandler() {
			public void onFocus(FocusEvent event) {
				numbers.setValue(false);
				usersByTag.setValue(false);
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
				numbers.setValue(false);
				usersByTag.setValue(false);
				usersByLog.setValue(true);
				
			}
		});
		
		sinceField.addFocusHandler(new FocusHandler() {
			
			public void onFocus(FocusEvent event) {
				since.setVisible(true);
				numbers.setValue(false);
				usersByTag.setValue(false);
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
//		file = new RadioButton("what","File:");
//		file.setFormValue("file");
//		sms = new RadioButton("what","SMS:");
//		sms.setFormValue("sms");
		survey = new RadioButton("what","Template:");
		survey.setFormValue("survey");
		CheckBox response = new CheckBox("Allow response");
		response.setName("response");
		
//		fileUpload = new FileUpload();
//  	fileUpload.setName("bcastfile");
//  	fileUpload.addChangeHandler(new ChangeHandler() {
//			public void onChange(ChangeEvent event) {
//				file.setValue(true);
//				sms.setValue(false);
//				survey.setValue(false);
//			}
//		});
  	TextArea smsArea = new TextArea();
  	smsArea.setName("sms");
  	smsArea.setSize("350px", "100px");
  	smsArea.addFocusHandler(new FocusHandler() {
			public void onFocus(FocusEvent event) {
				file.setValue(false);
				sms.setValue(true);
				survey.setValue(false);
			}
		});
  	surveys = new ListBox();
  	surveys.addItem("", "-1");
  	surveys.setName("survey");
  	surveys.addFocusHandler(new FocusHandler() {
			public void onFocus(FocusEvent event) {
				file.setValue(false);
				sms.setValue(false);
				survey.setValue(true);
			}
		});
//  	HorizontalPanel filePanel = new HorizontalPanel();
//  	filePanel.setSpacing(10);
//  	filePanel.add(file);
//  	filePanel.add(fileUpload);
  	
//  	HorizontalPanel smsPanel = new HorizontalPanel();
//  	smsPanel.setSpacing(10);
//  	smsPanel.add(sms);
//  	smsPanel.add(smsArea);
//  	// FOR NOW :-)
//  	sms.setEnabled(false);
//  	smsArea.setText("Coming soon!");
//  	smsArea.setEnabled(false);
  	
  	HorizontalPanel surveyPanel = new HorizontalPanel();
  	surveyPanel.setSpacing(10);
  	surveyPanel.add(survey);
  	surveyPanel.add(surveys);
  	surveyPanel.add(response);
  	
  	//what.add(filePanel);
  	what.add(surveyPanel);
  	//what.add(smsPanel);
  	
  	
  	HorizontalPanel whenPanel = new HorizontalPanel();
  	whenPanel.setSpacing(10);
  	Label note = new Label("NOTE: Calls are scheduled from the start time of the starting date in 10-minute intervals, 10 recipients at a time.");
  	note.setWidth("30%");
  	now = new RadioButton("when","Start now");
  	now.setFormValue("now");
  	now.addFocusHandler(new FocusHandler() {
			public void onFocus(FocusEvent event) {
				file.setValue(false);
				sms.setValue(false);
				survey.setValue(true);
			}
		});
		date = new RadioButton("when","Date:");
		date.setFormValue("date");
		
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
		
		HorizontalPanel ftDurationPanel = new HorizontalPanel();
		ftDurationPanel.setWidth("45%");
		ftDurationPanel.add(fromTillPanel);
		ftDurationPanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_RIGHT);
		ftDurationPanel.setVerticalAlignment(HasVerticalAlignment.ALIGN_MIDDLE);
		ftDurationPanel.add(durationLbl);
		ftDurationPanel.add(duration);
		ftDurationPanel.add(backups);
		
		when.add(nowPanel);
		when.add(datePanel);
		when.add(ftDurationPanel);
		
		stackPanel.add(who, createHeaderHTML(images.group(), "Recipients"), true);
		stackPanel.add(what, createHeaderHTML(images.messagesgroup(), "Message"), true);
		stackPanel.add(when, createHeaderHTML(images.calendar(), "Schedule"), true);
		
		controls = new HorizontalPanel();
		
		sendButton = new Button("Send", new ClickHandler() {
      public void onClick(ClickEvent event) {
      	setClickedButton();
      	Line line = Messages.get().getLine();
    		if (line != null) lineid.setValue(line.getId());
    		// just in case for fwded messages to get
    		// the params posted
    		survey.setEnabled(true);
    		surveys.setEnabled(true);
      	bcastForm.setAction(JSONRequest.BASE_URL + AoAPI.BCAST_MESSAGE);
        bcastForm.submit();
      }
    });
		cancelButton = new Button("Cancel");
		cancelButton.addClickHandler(new ClickHandler(){
			public void onClick(ClickEvent event) {
				// consistent (simple) behavior is to re-load
				// the first leaf in the shortcut we came from
				if (MessageForum.isMessageForum(backObj))
					Messages.get().displayMessages(new MessageForum(backObj));
				else
					// means we went to the bcast interface
					// directly from the link, so reload the bcast panel
					Messages.get().displaySurveyInput(null, 0);
			}
			
		});
		
		controls.setSpacing(10);
		controls.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_RIGHT);
		controls.add(cancelButton);
		controls.add(sendButton);
		
		outer.add(stackPanel);
		outer.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_RIGHT);
		outer.add(controls);
		lineid = new Hidden("lineid");
		outer.add(lineid);
		messageforumid = new Hidden("messageforumid");
		outer.add(messageforumid);
		
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
			Line line = Messages.get().getLine();
			JSONRequest request = new JSONRequest();
			String params = "";
			if (line != null)
				params = "?lineid=" + line.getId();
				
			request.doFetchURL(AoAPI.TAGS + params, new TagRequestor());
		}
	}
	
	public void loadSurveys()
	{
		Line line = Messages.get().getLine();
		JSONRequest request = new JSONRequest();
		String params = "";
		if (line != null)
			params = "?lineid=" + line.getId();
			
		request.doFetchURL(AoAPI.SURVEY + params, new SurveyRequestor());
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
	 
	 private class SurveyRequestor implements JSONRequester {
		 
			public void dataReceived(List<JSOModel> models) {
				Survey s;
				surveys.clear();
				surveys.addItem("", "-1");
				
				for (JSOModel model : models)
			  	{
						s = new Survey(model);
						surveys.addItem(s.getName(), s.getId());
			  	}

			}
	 }
	 
	 public void forwardThread(MessageForum mf)
	 {
		 messageforumid.setValue(mf.getId());
		 backObj = mf;
		 JSONRequest request = new JSONRequest();
		 request.doFetchURL(AoAPI.FORWARD_THREAD + mf.getId() + "/", new ForwardThreadRequestor());
		 
		 loadTags();
	 }
	 
	 private class ForwardThreadRequestor implements JSONRequester {
		 
			public void dataReceived(List<JSOModel> models) {
				Survey s;
				surveys.clear();
				
				for (JSOModel model : models)
			  	{
						s = new Survey(model);
						surveys.addItem(s.getName(), s.getId());
			  	}
				
				Messages.get().displayBroadcastPanel(backObj);
				setForwardingMode(true);
				if (surveys.getItemCount() == 1)
				{
					surveys.setEnabled(false);
					survey.setEnabled(false);
				}
				
			}
	 }
	 
	 private class BroadcastComplete implements SubmitCompleteHandler {
			
			public void onSubmitComplete(SubmitCompleteEvent event) {
				ConfirmDialog sent = new ConfirmDialog("Broadcast Scheduled!");
				sent.show();
				sent.center();
				
				sendComplete();
				Messages.get().loadBroadcasts();
				
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
	 
	 public void reset(BaseModel back)
	 {
		 bcastForm.reset();
		 backObj = back;
		 setForwardingMode(false);
		 // Select 7am-7pm by default
		 from.setItemSelected(6, true);
		 till.setItemSelected(18, true);
		 lastNCallers.setItemSelected(3, true);
		 duration.setItemSelected(1,true);
		 
		 Date tomorrow = new Date();
		 // It's deprecated but GWT has no better way
		 tomorrow.setDate(tomorrow.getDate() + 1);
		 bcastDateField.setValue(DateTimeFormat.getFormat("MMM-dd-yyyy").format(tomorrow));
		 date.setValue(true);
		 
		 stackPanel.showStack(0);
	 }
	 
  private void setForwardingMode(boolean fwdMode)
  {
//	 file.setEnabled(!fwdMode);
//	 fileUpload.setEnabled(!fwdMode);
	 survey.setValue(fwdMode);
	 // set these to true/0 no matter what and
	 // let the special case disable if needed
	 surveys.setEnabled(true);
	 survey.setEnabled(true);
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
