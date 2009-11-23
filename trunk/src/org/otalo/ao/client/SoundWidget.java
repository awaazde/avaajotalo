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
