import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { LoginComponent } from './components/login.component';
import { UnAuthGuard } from './guards/unauth-guard';

const routes: Routes = [
  { path: '', component: LoginComponent, canActivate: [UnAuthGuard], pathMatch: 'full' }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
  providers: []
})
export class AuthRoutingModule { }
