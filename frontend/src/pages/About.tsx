import { Link } from 'react-router'
import Seal from '../components/Seal.tsx'
import { FOUNDED } from '../data/shop.ts'
import { usePageTitle } from '../usePageTitle.ts'

const SERVICES = [
  { name: 'Screen printing', detail: 'Large runs for teams, clubs, reunions, and departments.' },
  { name: 'Embroidery', detail: 'Crests and logos stitched to last for years of wear.' },
  { name: 'Custom web stores', detail: 'Online shops for your group, with fulfillment handled for you.' },
  { name: 'Graphic design', detail: 'Help turning a rough idea into a design that prints well.' },
  { name: 'Event merchandise', detail: 'Everything for game day, commencement, and the big weekend.' },
]

const VALUES = [
  {
    name: 'Service comes first',
    detail: 'You get a real person who knows the shop, whether you walk in or write in.',
  },
  {
    name: 'Straight dealing',
    detail: 'Fair prices, honest timelines, and no surprises when the order arrives.',
  },
  {
    name: 'In it for the long run',
    detail: "We'd rather earn a customer for life than make a quick sale.",
  },
]

export default function About() {
  usePageTitle('About Us')

  return (
    <>
      <section className="page-hero">
        <div className="container">
          <p className="eyebrow eyebrow--light">About us</p>
          <h1>Same corner. Same family. Since {FOUNDED}.</h1>
          <p className="page-hero__lede">
            Campus Customs began as a small Yale memorabilia shop across the street from campus. More than fifty
            years later, it's still right there, and still in the family.
          </p>
        </div>
      </section>

      <section className="section">
        <div className="container split">
          <div className="split__copy">
            <p className="eyebrow">Where it started</p>
            <h2>One storefront, one big idea</h2>
            <p>
              In {FOUNDED}, our father opened a shop for anyone who wanted to carry a little Yale home with them.
              He believed good service is what brings people back, and he ran the place that way every day.
            </p>
            <p>
              He's retired now, and his sons run the business. The storefront hasn't moved an inch, and his way of
              doing things hasn't changed either.
            </p>
          </div>
          <div className="split__media">
            <Seal className="seal--navy" />
          </div>
        </div>
      </section>

      <section className="section section--tinted" id="services" aria-labelledby="services-heading">
        <div className="container">
          <header className="section__header">
            <p className="eyebrow">More than a storefront</p>
            <h2 id="services-heading">We make it, too</h2>
            <p>
              Our production shop sits right next door to the original store. Because design, printing, and
              shipping all happen under one roof, orders turn around fast without losing the personal touch.
            </p>
          </header>
          <ul className="service-list">
            {SERVICES.map((service) => (
              <li key={service.name}>
                <h3>{service.name}</h3>
                <p>{service.detail}</p>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <header className="section__header">
            <p className="eyebrow">What we stand for</p>
            <h2>How we do business</h2>
          </header>
          <ul className="value-grid">
            {VALUES.map((value, index) => (
              <li key={value.name} className="value-card">
                <span className="value-card__number" aria-hidden="true">
                  {String(index + 1).padStart(2, '0')}
                </span>
                <h3>{value.name}</h3>
                <p>{value.detail}</p>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="cta-band">
        <div className="container cta-band__inner">
          <div>
            <h2>Come see the collection.</h2>
            <p>Crewnecks, hoodies, tees, and more for every college, school, and team.</p>
          </div>
          <Link to="/products" className="button button--light">
            Shop products
          </Link>
        </div>
      </section>
    </>
  )
}
