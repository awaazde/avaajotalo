package org.otalo.ao.client.model;

public class MessageTag extends BaseModel {
	
	public MessageTag(JSOModel data) {
		super(data);
	}
	
	public Tag getTag()
	{
		return new Tag(getObject("fields").getObject("tag"));
	}

}
