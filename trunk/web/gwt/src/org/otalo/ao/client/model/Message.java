package org.otalo.ao.client.model;


public class Message extends BaseModel {

	/* Order matters. The constants are mirrored in 
	 * server side code. The ordinal value of the first declared
	 * is 0 and then increases from there.
	 */
	public enum MessageStatus {
		PENDING, APPROVED, REJECTED
	}
	
	public boolean read;
	
	public Message(JSOModel data) {
		super(data);
	}
	
	public String getDate()
	{
		return getObject("fields").get("date");
	}
	
	public User getAuthor()
	{
		return new User(getObject("fields").getObject("user"));
	}
	
	public String getContent()
	{
//	SimpleDateFormat format = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
//	return format.parse(dateStr);
		return getObject("fields").get("content_file");
	}
	
	public String getRgt()
	{
		return getObject("fields").get("rgt");
	}
	
	public String getLft()
	{
		return getObject("fields").get("lft");
	}
		
}
