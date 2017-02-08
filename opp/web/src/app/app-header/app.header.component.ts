import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output, OnInit } from '@angular/core';
import { FormControl, Validators } from '@angular/forms';
import 'rxjs/add/operator/debounceTime';


@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
  selector: 'app-header',
  templateUrl: './app.header.component.html',
  styleUrls: ['./app.header.component.scss']
})

export class AppHeaderComponent implements OnInit {
  @Input() loggedIn: boolean;
  @Output() logout = new EventEmitter(false);
  @Output() secretPhraseChange = new EventEmitter(false);

  secretPhrase: FormControl;

  ngOnInit() {
    this.secretPhrase = new FormControl('', [Validators.required, Validators.minLength(6)]);
    this.secretPhrase.valueChanges
      .debounceTime(500)
      .subscribe((newValue) => {
        if (this.secretPhrase.valid) {
          this.secretPhraseChange.emit(newValue);
        }
      });
  }
}
