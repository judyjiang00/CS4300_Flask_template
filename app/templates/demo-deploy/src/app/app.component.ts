import { Component, OnInit } from '@angular/core';
import { Query } from './query'

@Component({
	selector: 'query-sel',
	templateUrl: './app.component.html',
	styleUrls: ['./app.component.css']
})
export class AppComponent {
	title = 'Travel App'; 
	show_query = true; 
	query = new Query ("", "", ""); 

  //user has clicked on search button
  onEntered(){
  	//client-side query preprocessing/expansion
  	
  	//remove query_page from view
  	this.show_query = false
  	
  }

}
