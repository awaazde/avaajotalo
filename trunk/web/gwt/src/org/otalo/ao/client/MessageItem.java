/*
 * Copyright 2007 Google Inc.
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

import java.util.Date;

/**
 * A simple structure containing the basic components of a message.
 */
public final class MessageItem {

  /**
   * Message date
   */
  public Date date;
  
  /**
   * message status
   */
  public String status;

  /**
   * Phone number
   */
  public String caller;


  /**
   * question and answers
   */
  public String questionFile;
  
  public String responseFile;

  /**
   * Read flag.
   */
  public boolean read;

  public MessageItem(Date date, String caller, String questionFile) {
    this.date = date;
    //this.status = status;
    this.caller = caller;
    this.questionFile = questionFile;
    //this.responseFile = responseFile;
  }
}
