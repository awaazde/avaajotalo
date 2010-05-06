/*
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
