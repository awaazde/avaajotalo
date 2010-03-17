package org.otalo.ao.client;

import org.otalo.ao.client.model.MessageForum;

import com.google.gwt.user.client.ui.Composite;

/**
 * Implement the interface for tagging messages here. Depending on your requirements,
 * this can be an empty textfield, some number of combo boxes, or something else.
 * @author neil
 *
 */
public abstract class TagWidget extends Composite {
	public abstract void loadSelectedTags(MessageForum messageForun);
	public abstract String getErrorText();
	public abstract void reset();
}
