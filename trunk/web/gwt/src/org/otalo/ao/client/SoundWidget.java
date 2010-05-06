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

import com.google.gwt.user.client.ui.HTML;

public class SoundWidget {

	private HTML sound;
	
	public SoundWidget(String filename)
	{
		sound = new HTML("<object width=\"200\" height=\"24\" type=\"application/x-shockwave-flash\" data=\"ao/swf/player.swf\" id=\"audioplayer2\">"  +
    "<param name=\"movie\" value=\"ao/swf/player.swf\" />" +
    "<param name=\"FlashVars\" value=\"playerID=2&amp;soundFile=" + filename +"\"  />" +
    "<param name=\"quality\" value=\"high\" />" +
    "<param name=\"menu\" value=\"false\" />" +
    "<param name=\"wmode\" value=\"transparent\" /> </object>");
		
	}
	
	public HTML getWidget()
	{
		return sound;
	}
}
