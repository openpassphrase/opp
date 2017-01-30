import { OppWebPage } from './app.po';

describe('opp-web App', function() {
  let page: OppWebPage;

  beforeEach(() => {
    page = new OppWebPage();
  });

  it('should display message saying app works', () => {
    page.navigateTo();
    expect(page.getParagraphText()).toEqual('app works!');
  });
});
