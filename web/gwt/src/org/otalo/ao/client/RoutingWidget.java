package org.otalo.ao.client;

import org.otalo.ao.client.model.MessageForum;

import com.google.gwt.user.client.ui.Composite;

/**
 * Implement the interface for routing messages here. Depending on your requirements,
 * this can be a read-only list, multi-select list, or something else.
 * @author neil
 *
 */
public abstract class RoutingWidget extends Composite {
	public abstract void loadRoutingInfo(MessageForum messageForum);
	public abstract void reset();
}
