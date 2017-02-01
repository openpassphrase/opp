import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';


@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
  selector: 'app-header',
  templateUrl: './app.header.component.html'
})

export class AppHeaderComponent {
  @Input() loggedIn: boolean;
  @Output() logout = new EventEmitter(false);
}
