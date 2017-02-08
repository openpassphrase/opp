import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpModule } from '@angular/http';
import { ReactiveFormsModule } from '@angular/forms';
import { MaterialModule } from '@angular/material';
import { FlexLayoutModule } from '@angular/flex-layout';

import { StoreModule } from '@ngrx/store';
import { EffectsModule } from '@ngrx/effects';

import { AppRoutingModule } from './app-routing.module';
import { AuthModule } from './auth/auth.module';
import { PasswordsModule } from './passwords/passwords.module';

import { AppComponent } from './app.component';
import { AppHeaderComponent } from './app-header/app.header.component';

import { reducer } from './reducers';
import { CategoryEffects } from './effects/categories';
import { ItemEffects } from './effects/items';

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
    PasswordsModule,
    ReactiveFormsModule,
    StoreModule.provideStore(reducer),
    EffectsModule.run(CategoryEffects),
    EffectsModule.run(ItemEffects),
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
