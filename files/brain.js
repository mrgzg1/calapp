
var gcal = {
  clientId: '526830948367-u5oq7mbudslpl0ss20ukdot8m8mijjlq',
  apiKey: 'AIzaSyBItmgNX0SaWe5_fKVGe6BWa_R2LHXCI2o',
  scopes: 'https://www.googleapis.com/auth/calendar',

  controller: function(){
    $('#googlePart').show();
  },

  //called once the google api has been loaded
  handleClientLoad: function() {
    gapi.client.setApiKey(apiKey);
    window.setTimeout(this.checkAuth,1);
  },

  //checks authorization
  checkAuth: function() {
    gapi.auth.authorize({client_id: clientId, scope: scopes, immediate: true},
        handleAuthResult);
  },

  //handles the authrization response
  handleAuthResult:function(authResult) {
    if (authResult) {
      $('#gauthButton').hide();
      gcal.loadCalApi();
      return true;
    } else {
      console.log("not authorized");
      //do whatever for when not authorized
      return false;
     }
  },

  //initializes the authentication call
  handleAuthClick:function(event) {
    gapi.auth.authorize(
        {client_id: this.clientId, scope: this.scopes, immediate: false},
        this.handleAuthResult);
    return false;
  },

  //load the calendar api
  loadCalApi:function() {
    gapi.client.load('calendar', 'v3', gcal.handleCalApiLoad);
  },

  //called after the api has been loaded
  handleCalApiLoad: function(){
    var name = prompt('Please give a name to class calendar')
    gcal.createCalendar(name,gcal.insertClasses);
  },
  //custom function that call
  insertClasses: function(resp){
    var flag = true;
    $.each(app.courseData, function(i, each){
      flag = flag & gcal.insertRecurEvent(resp.id, each, gcal.afterInsertHandler);
    });
    $('#googlePart').hide();
    $('#final').show();
  },
  afterInsertHandler:function(resp){
    var target = $('#final');
    if(resp.creator)
      target.append('<p>'+resp.summary+' has been inserted</p>');
    else
      target.append('<p> something went wrong here, try again and if problem persists please email me</p>');
    if(target.find('p').length == app.courseData.length)
      target.append('<p> done :)');
  },
  //creates a calendar with name passed as the first arg and callback function as second
  //calls back the callback function with result object
  createCalendar: function(name, callback){
    var request = gapi.client.calendar.calendars.insert({
      resource:{summary:name}
    });
    request.execute(function(resp){
      if(resp.result.summary == name){
        if(callback != null)
          callback(resp.result);
        else
          console.log(resp);
        return true;
      }
      else{
        console.log('something went wrong');
        return false;
      }
    });
  },
  insertRecurEvent:function(calendar, event, callback){
    var options = {
      calendarId:calendar,
      resource:{
        end:{
          dateTime: event.end_time,
          timeZone: "America/Chicago"
        },
        start:{
          dateTime: event.start_time,
          timeZone: "America/Chicago"
        },
        summary: event.course,
        location: event.location,
        recurrence:["RRULE:FREQ=WEEKLY;WKST=SU;BYDAY="+event.days+";UNTIL="+event.end_date]
      }
    };
    console.log(options);
    var request = gapi.client.calendar.events.insert(options);
    request.execute(function(resp){
      console.log(resp);
      callback(resp);  
    });
  }
};

var enterprise = {
  controller:function(){
    $('#enterprisePart').show();
    $('#loading').hide();
    this.formInit();
  },
  formInit:function(){
    $('#enterpriseCred').magicForm({
      'url':'/enterprise',
      'success':this.entFormSuccess,
      'loading':this.loading
    });
  },
  loading: function(){
    $('#enterpriseCred').hide();
    $('#results').hide();
    $('#loading').show();
  },
  entFormSuccess: function(data){
    app.courseData = $.parseJSON(data)
    if(app.courseData == null){
      $('#results').show();
      $("#results").html('Invalid Credentials');
      $('#enterpriseCred').show();
      $('#loading').hide();
    }
    //exit function for this part
    else{
      $('#enterprisePart').hide();
      gcal.controller();//hand over the control to google part
    }
  }
};

var app = {
  init: function(){
    $('section').hide();
    enterprise.controller();
  },
}

app.init();
