package org.otalo.ao.client.model;

public class Tag extends BaseModel {
	
	public Tag(JSOModel data) {
		super(data);
	}
	
	public String getType() {
		return getObject("fields").get("type");
	}
	
	public String getTag() {
		return getObject("fields").get("tag");
	}

}
