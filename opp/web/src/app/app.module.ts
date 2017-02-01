import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpModule } from '@angular/http';
import { MaterialModule } from '@angular/material';
import { FlexLayoutModule } from '@angular/flex-layout';
import { AppRoutingModule } from './app-routing.module';
import { AuthModule } from './auth/auth.module';
import { PasswordsModule } from './passwords/passwords.module';

import { AppComponent } from './app.component';
import { AppHeaderComponent } from './app-header/app.header.component';

@NgModule({
  declarations: [
    AppComponent,
    AppHeaderComponent
  ],
  imports: [
    BrowserModule,
    HttpModule,
    AppRoutingModule,
    MaterialModule.forRoot(),
    FlexLayoutModule.forRoot(),
    AuthModule,
    PasswordsModule
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
