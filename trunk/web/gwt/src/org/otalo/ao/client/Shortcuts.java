/*
 * Copyright 2008 Google Inc.
 * Copyright (c) 2009 Regents of the University of California, Stanford University, and others
 * 
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not
 * use this file except in compliance with the License. You may obtain a copy of
 * the License at
 * 
 * http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations under
 * the License.
 */
package org.otalo.ao.client;

import com.google.gwt.resources.client.ImageResource;
import com.google.gwt.user.client.ui.AbstractImagePrototype;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.DecoratedStackPanel;
import com.google.gwt.user.client.ui.Widget;

/**
 * A composite that contains the shortcut stack panel on the left side. The
 * mailbox tree and shortcut lists don't actually do anything, but serve to show
 * how you can construct an interface using
 * {@link com.google.gwt.user.client.ui.StackPanel},
 * {@link com.google.gwt.user.client.ui.Tree}, and other custom widgets.
 */
public class Shortcuts extends Composite {

	/**
	 * An image bundle specifying the images for this Widget and aggragating
	 * images needed in child widgets.
	 */
	public interface Images extends Fora.Images {
		ImageResource forum();
	}

	private int nextHeaderIndex = 0;
	private DecoratedStackPanel stackPanel = new DecoratedStackPanel();

	/**
	 * Constructs a new shortcuts widget using the specified images.
	 * 
	 * @param images
	 *            a bundle that provides the images for this widget
	 */
	public Shortcuts(Images images, Fora fora) {
		add(fora, images.forum(), "Forums");
		initWidget(stackPanel);
	}

	@Override
	protected void onLoad() {
		// Show the messages group by default.
		stackPanel.showStack(0);
	}

	private void add(Widget widget, ImageResource resource,
			String caption) {
		widget.addStyleName("mail-StackContent");
		stackPanel.add(widget, createHeaderHTML(resource, caption), true);
	}

	/**
	 * Creates an HTML fragment that places an image & caption together, for use
	 * in a group header.
	 * 
	 * @param imageProto
	 *            an image prototype for an image
	 * @param caption
	 *            the group caption
	 * @return the header HTML fragment
	 */
	private String createHeaderHTML(ImageResource resource,
			String caption) {
		nextHeaderIndex++;
		AbstractImagePrototype imageProto = AbstractImagePrototype.create(resource);
		String captionHTML = "<table class='caption' cellpadding='0' cellspacing='0'>"
				+ "<tr><td class='lcaption'>"
				+ imageProto.getHTML()
				+ "</td><td class='rcaption'><b style='white-space:nowrap'>"
				+ caption + "</b></td></tr></table>";
		return captionHTML;
	}

	
}
