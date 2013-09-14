/*
 * Copyright 2013 Google Inc.
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
package org.otalo.ao.client.search;

import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.DockPanel;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.VerticalPanel;

/**
 * A composite for displaying the details of a voice message.
 */
public class ROMessageDetail extends Composite {
	private Button editButton;
	private VerticalPanel thread;
	private HorizontalPanel outer;
	private DockPanel threadPanel;
	private FlexTable detailsTable;
	private CheckBox sticky;
	private Label tags;
	private Label routing;
		
	public ROMessageDetail() {
		outer = new HorizontalPanel();
	  	outer.setSize("100%", "100%");
	  	threadPanel = new DockPanel();
	  	detailsTable = new FlexTable();
	  	tags = new Label();
	  	routing = new Label();
	  	
	}
}
