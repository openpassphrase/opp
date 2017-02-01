import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MaterialModule } from '@angular/material';
import { FlexLayoutModule } from '@angular/flex-layout';
import { ReactiveFormsModule } from '@angular/forms';

import { AuthRoutingModule } from './auth-routing.module';
import { LoginComponent } from './components/login.component';
import { Auth } from './services/auth.service';
import { AuthGuard } from './guards/auth-guard';
import { UnAuthGuard } from './guards/unauth-guard';

@NgModule({
  imports: [
    CommonModule,
    MaterialModule,
    FlexLayoutModule,
    ReactiveFormsModule,
    AuthRoutingModule
  ],
  declarations: [
    LoginComponent
  ],
  providers: [
    Auth,
    AuthGuard,
    UnAuthGuard
  ]
})
export class AuthModule { }

export { Auth }
export { AuthGuard }
export { UnAuthGuard }
