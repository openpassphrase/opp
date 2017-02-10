import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpModule, Http, RequestOptions, BaseRequestOptions } from '@angular/http';
import { ReactiveFormsModule } from '@angular/forms';
import { MaterialModule } from '@angular/material';
import { FlexLayoutModule } from '@angular/flex-layout';
import { AuthHttp, AuthConfig } from 'angular2-jwt';
import { ClipboardModule } from 'ngx-clipboard';
import { PasswordsRoutingModule } from './passwords-routing.module';
import { PasswordsComponent } from './passwords.component';
import { BackendService } from './services/backend.service';
import { AddCategoryFormComponent } from './components/add-category-form/add-category-form.component';
import { CategoryComponent, DeleteCategoryDialogComponent } from './components/category/category.component';
import { ItemComponent, DeleteItemDialogComponent } from './components/item/item.component';
import { ItemFormComponent } from './components/item-form/item-form.component';
import { Auth } from '../auth/auth.module';

export function authHttpServiceFactory(http: Http, options: RequestOptions) {
  return new AuthHttp(new AuthConfig({
    headerName: 'x-opp-jwt',
    noTokenScheme: true
  }), http, options);
}

@NgModule({
  imports: [
    CommonModule,
    PasswordsRoutingModule,
    ReactiveFormsModule,
    MaterialModule,
    FlexLayoutModule,
    ClipboardModule
  ],
  declarations: [
    PasswordsComponent,
    AddCategoryFormComponent,
    CategoryComponent,
    DeleteCategoryDialogComponent,
    ItemComponent,
    ItemFormComponent,
    DeleteItemDialogComponent
  ],
  providers: [
    BackendService,
    {
      provide: AuthHttp,
      useFactory: authHttpServiceFactory,
      deps: [Http, RequestOptions]
    }
  ],
  entryComponents: [
    DeleteCategoryDialogComponent,
    ItemFormComponent,
    DeleteItemDialogComponent
  ]
})
export class PasswordsModule { }
