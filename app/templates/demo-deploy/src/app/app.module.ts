import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppComponent } from './app.component';
import { FormsModule } from '@angular/forms';
import { FilterComponent } from './filter-view/filter-view.component'; 

@NgModule({
  declarations: [
    AppComponent, 
    FilterComponent
  ],
  imports: [
    BrowserModule, 
    FormsModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
