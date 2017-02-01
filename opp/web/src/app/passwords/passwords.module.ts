import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpModule, Http, RequestOptions } from '@angular/http';
import { ReactiveFormsModule } from '@angular/forms';
import { MaterialModule } from '@angular/material';
import { FlexLayoutModule } from '@angular/flex-layout';
import { AuthHttp, AuthConfig } from 'angular2-jwt';
import { PasswordsRoutingModule } from './passwords-routing.module';
import { PasswordsComponent } from './passwords.component';
import { BackendService } from './services/backend.service';
import { StoreService } from './services/store.service';
import { AddCategoryFormComponent } from './components/add-category-form/add-category-form.component';
import { CategoryListComponent } from './components/category-list/category-list.component';

export function authHttpServiceFactory(http: Http, options: RequestOptions) {
  return new AuthHttp(new AuthConfig({
    headerName: 'x-opp-jwt',
    noTokenScheme: true,
    globalHeaders: [{'x-opp-phrase': 'my-secret-phrase-is-awesome'}]
  }), http, options);
}

@NgModule({
  imports: [
    CommonModule,
    PasswordsRoutingModule,
    ReactiveFormsModule,
    MaterialModule,
    FlexLayoutModule
  ],
  declarations: [
    PasswordsComponent,
    AddCategoryFormComponent,
    CategoryListComponent
  ],
  providers: [
    BackendService,
    StoreService,
    {
      provide: AuthHttp,
      useFactory: authHttpServiceFactory,
      deps: [Http, RequestOptions]
    }
  ]
})
export class PasswordsModule { }
