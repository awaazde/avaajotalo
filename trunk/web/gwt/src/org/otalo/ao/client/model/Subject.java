package org.otalo.ao.client.model;

public class Subject extends BaseModel {

	public Subject(JSOModel data) {
		super(data);
	}
	
	public String getName()
	{
		return getField("name");
	}
	
	public String getNumber()
	{
		return getField("number");
	}

}
