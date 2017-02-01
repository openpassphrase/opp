import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { PasswordsComponent } from './passwords.component';
import { AuthGuard } from '../auth/auth.module';

const routes: Routes = [
  { path: 'passwords', component: PasswordsComponent, canActivate: [AuthGuard] }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
  providers: []
})
export class PasswordsRoutingModule { }
