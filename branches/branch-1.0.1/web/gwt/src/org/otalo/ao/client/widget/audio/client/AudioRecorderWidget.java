package org.otalo.ao.client.widget.audio.client;

import org.otalo.ao.client.ConfirmDialog;
import org.otalo.ao.client.JSONRequest;
import org.otalo.ao.client.Messages;
import org.otalo.ao.client.JSONRequest.AoAPI.ValidationError;
import org.otalo.ao.client.model.JSOModel;
import org.otalo.ao.client.model.MessageForum;
import org.otalo.ao.client.widget.audio.resource.CustomButton;
import org.otalo.ao.client.widget.audio.resource.ResourceBundle;

import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.core.client.JsArray;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.resources.client.ImageResource;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.Label;

/**
 * AudioRecorderWidget provides audio recording functionality into application
 */
public class AudioRecorderWidget extends Composite implements ClickHandler  {

	//player button icons
	private ImageResource playIcon = ResourceBundle.INSTANCE.play();
	private ImageResource stopIcon = ResourceBundle.INSTANCE.stop();
	private ImageResource recordIcon = ResourceBundle.INSTANCE.record();

	private CustomButton playButton;
	private CustomButton recordButton;
	private CustomButton stopButton;

	public String uploadURL;
	public JsArray jsStrings;
	private Label status;
	boolean isRecorded;

	private RecorderEventObserver recorderEventObserver;

	public AudioRecorderWidget(String uploadURL, RecorderEventObserver eventObserver) {
		this.uploadURL = uploadURL;
		this.jsStrings = JavaScriptObject.createArray().cast();
		this.recorderEventObserver = eventObserver;
		FlexTable outer = new FlexTable();

		//creating play button 
		playButton = new CustomButton();
		playButton.setResource(playIcon);
		playButton.setText("Play");
		//binding click event
		playButton.addClickHandler(this);
		playButton.setEnabled(false);

		//creating record button 
		recordButton = new CustomButton();
		recordButton.setResource(recordIcon);
		recordButton.setText("Record");
		//binding click event
		recordButton.addClickHandler(this);

		//creating stop button 
		stopButton = new CustomButton();
		stopButton.setResource(stopIcon);
		stopButton.setText("Stop");
		//binding click event
		stopButton.addClickHandler(this);
		stopButton.setEnabled(false);

		status = new Label("Click on record button to start recording...");
		status.getElement().setId("status-lbl");
		status.addStyleName("label-txt");
		outer.setWidget(0, 0, recordButton);
		outer.setWidget(0, 1, playButton);
		outer.setWidget(0, 2, stopButton);
		//outer.getFlexCellFormatter().setColSpan(1, 0, 3);
		outer.setWidget(0, 3, status);

		isRecorded = false;
		initWidget(outer);
	}

	/**
	 * Uploads data to server
	 */
	public void uploadData(AudioRecordParam [] paramData) {
		for (AudioRecordParam param : paramData) {
			AudioRecordJsParam jsParam = (AudioRecordJsParam) JavaScriptObject.createObject().cast();
			jsParam.setName(param.getName());
			jsParam.setValue(param.getValue());
			this.jsStrings.push(jsParam);
		}
		onSaveButtonClick(this.uploadURL, this.jsStrings, this);
	}
	
	static class AudioRecordJsParam extends JavaScriptObject {
		protected AudioRecordJsParam() { }
		/**
		 * @return the name
		 */
		public final native String getName() /*-{
			return this.name;
		}-*/;
		
		/**
		 * @param name the name to set
		 */
		public final native void setName(String name) /*-{ 
			this.name = name;
		}-*/;
		
		/**
		 * @return the value
		 */
		public final native String getvalue() /*-{
			return this.value;
		}-*/;
		
		/**
		 * @param name the name to set
		 */
		public final native void setValue(String value) /*-{ 
			this.value = value;
		}-*/;
	}
		

	public static native void onPlayButtonClick() /*-{
		$wnd.play();
	}-*/;

	public static native void onStopButtonClick() /*-{
		$wnd.stop();
	}-*/;

	public static native void onRecordButtonClick() /*-{
		$wnd.record();
	}-*/;

	public static native void onSaveButtonClick(String url, JsArray params, AudioRecorderWidget widget) /*-{
		$wnd.onAudioSucessCallBack = $entry(function(responseData) {
      		widget.@org.otalo.ao.client.widget.audio.client.AudioRecorderWidget::onSuccess(Ljava/lang/String;)(responseData);
    	});
		
		
		$wnd.onAudioErrorCallBack = $entry(function(responseData) {
      		widget.@org.otalo.ao.client.widget.audio.client.AudioRecorderWidget::onError(Ljava/lang/String;)(responseData);
    	});
		
		$wnd.upload(url, params);
	}-*/;
	
	
	public void onSuccess(String data) {
		JSOModel model = JSONRequest.getModels(data).get(0);
		recorderEventObserver.onRecordSuccess(model);
	}

	public void onError(String errorData) {
		recorderEventObserver.onRecordError(errorData);
	}

	
	public void onClick(ClickEvent event) {
		Object sender = event.getSource();
		if (sender == playButton) {
			//play is clicked
			onPlayButtonClick();
		} else if(sender == recordButton) {
			//record is clicked
			stopButton.setEnabled(true);
			isRecorded = true;
			recorderEventObserver.recordStart();
			onRecordButtonClick();
		} else if(sender == stopButton) {
			playButton.setEnabled(true);
			onStopButtonClick();
		}
	}

	public void setEnabled(boolean isEnable) {
		if(isRecorded && isEnable)
			playButton.setEnabled(true);
		else
			playButton.setEnabled(false);

		if(isRecorded && isEnable)
			stopButton.setEnabled(true);
		else
			stopButton.setEnabled(false);

		recordButton.setEnabled(isEnable);
		if(!isEnable) {
			status.removeStyleName("normal-text");
			status.addStyleName("gray-text");
		}
		else {
			status.removeStyleName("gray-text");
			status.addStyleName("normal-text");
		}
	}

	/**
	 * @return the uploadURL
	 */
	public String getUploadURL() {
		return uploadURL;
	}

	/**
	 * @param uploadURL the uploadURL to set
	 */
	public void setUploadURL(String uploadURL) {
		this.uploadURL = uploadURL;
	}

	/**
	 * @return the isRecorded
	 */
	public boolean isRecorded() {
		return isRecorded;
	}
}
