import { Directive, ElementRef, EventEmitter, HostListener, Output } from '@angular/core';

@Directive({
  selector: '[clickOutside]',
  standalone: true
})
export class ClickOutsideDirective {
  @Output() clickOutside = new EventEmitter<Event>();

  constructor(private elementRef: ElementRef) { }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: Event): void {
    const isClickedInside = this.elementRef.nativeElement.contains(event.target);
    if (!isClickedInside) {
      this.clickOutside.emit(event);
    }
  }
}
