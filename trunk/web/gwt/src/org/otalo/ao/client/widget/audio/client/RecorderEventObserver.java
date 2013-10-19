/**
 * 
 */
package org.otalo.ao.client.widget.audio.client;

import org.otalo.ao.client.JSONRequest.AoAPI.ValidationError;
import org.otalo.ao.client.model.JSOModel;

/**
 * @author nikhil
 *
 */
public interface RecorderEventObserver {

	/**
	 * Indicates that recording is started
	 */
	public void recordStart();
	
	/**
	 * Would be called if record request is successfully get submitted
	 */
	public void onRecordSuccess(JSOModel model);
	
	/**
	 * Would be called if record request is not successfully get submitted
	 */
	public void onRecordError(String msg);
}
