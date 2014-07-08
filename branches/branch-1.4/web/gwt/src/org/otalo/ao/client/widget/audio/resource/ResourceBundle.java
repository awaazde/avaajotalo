package org.otalo.ao.client.widget.audio.resource;

import com.google.gwt.core.client.GWT;
import com.google.gwt.resources.client.ClientBundle;
import com.google.gwt.resources.client.ImageResource;

public interface ResourceBundle extends ClientBundle {

	public static ResourceBundle INSTANCE = GWT.create(ResourceBundle.class);

	@Source("play.png")
	ImageResource play();	

	@Source("stop.png")
	ImageResource stop();
	
	@Source("record.png")
	ImageResource record();

}
