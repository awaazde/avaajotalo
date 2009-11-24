package org.otalo.ao.client;

import java.util.List;

import org.otalo.ao.client.model.JSOModel;

public interface JSONRequester {
	public void dataReceived (List<JSOModel> models);
}
