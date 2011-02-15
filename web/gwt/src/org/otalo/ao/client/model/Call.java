package org.otalo.ao.client.model;

public class Call extends BaseModel {

	public Call(JSOModel data) 
	{
		super(data);
	}

	public Subject getSubject()
	{
		return new Subject(getObject("fields").getObject("subject"));
	}
	
	public String getDate()
	{
		return getObject("fields").get("date");
	}
}
