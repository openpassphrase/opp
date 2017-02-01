import { Component, Input, Output, EventEmitter } from '@angular/core';
import { ICategory } from '../../models/category';

@Component({
  selector: 'app-category-list',
  templateUrl: './category-list.component.html',
  styleUrls: ['./category-list.component.scss']
})
export class CategoryListComponent {
  @Input() categories: ICategory[];
  @Output() remove = new EventEmitter(false);
  @Output() update = new EventEmitter(false);

  constructor() { }
}
