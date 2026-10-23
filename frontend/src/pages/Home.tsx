import { Link } from 'react-router'
import type { PointerEvent } from 'react'
import Seal from '../components/Seal.tsx'
import Skyline from '../components/Skyline.tsx'
import { COLLECTIONS, FOUNDED, PRODUCT_COUNT } from '../data/shop.ts'
import { usePageTitle } from '../usePageTitle.ts'

const yearsOpen = new Date().getFullYear() - FOUNDED

// A soft pool of light follows the pointer across the hero, like a lantern in the dark.
function moveLantern(event: PointerEvent<HTMLElement>) {
  const box = event.currentTarget.getBoundingClientRect()
  event.currentTarget.style.setProperty('--lantern-x', `${event.clientX - box.left}px`)
  event.currentTarget.style.setProperty('--lantern-y', `${event.clientY - box.top}px`)
}

export default function Home() {
  usePageTitle()

  return (
    <>
      <section className="hero" onPointerMove={moveLantern}>
        <Skyline />
        <div className="container hero__inner">
          <div className="hero__copy">
            <p className="eyebrow eyebrow--light">New Haven, Connecticut · Est. {FOUNDED}</p>
            <h1>
              <span className="hero__line">When the elms</span> <span className="hero__line">glow blue,</span>{' '}
              <span className="hero__accent">the shop's still lit.</span>
            </h1>
            <p className="hero__lede">
              Since {FOUNDED}, the shop across the street from Old Campus has dressed students, alumni, and the
              families cheering them on. Hoodies, crewnecks, quarter-zips, and tees, lit up and ready.
            </p>
            <div className="hero__actions">
              <Link to="/products" className="button button--light">
                Shop the collection
              </Link>
              <Link to="/about" className="button button--ghost-light">
                Our story
              </Link>
            </div>
          </div>
          <div className="hero__badge">
            <Seal />
          </div>
        </div>
      </section>

      <section className="stats" aria-label="Campus Customs at a glance">
        <ul className="container stats__list">
          <li>
            <strong>{yearsOpen}+</strong>
            <span>years across from campus</span>
          </li>
          <li>
            <strong>{PRODUCT_COUNT}</strong>
            <span>Yale styles in the shop</span>
          </li>
          <li>
            <strong>XS–XXL</strong>
            <span>in every single style</span>
          </li>
          <li>
            <strong>11</strong>
            <span>residential college crests</span>
          </li>
        </ul>
      </section>

      <section className="section">
        <div className="container">
          <header className="section__header">
            <p className="eyebrow">Shop by collection</p>
            <h2>Something for every corner of campus</h2>
            <p>
              Whether you live in Saybrook, study at the law school, row on the Housatonic, or just raised someone
              who does, there's a crest with your name on it.
            </p>
          </header>
          <ul className="tile-grid">
            {COLLECTIONS.map((collection) => (
              <li key={collection.name}>
                <Link to="/products" className="tile">
                  <span className="pill">{collection.tag}</span>
                  <h3>{collection.name}</h3>
                  <p>{collection.blurb}</p>
                  <span className="tile__cta" aria-hidden="true">
                    Browse →
                  </span>
                </Link>
              </li>
            ))}
            <li>
              <Link to="/products" className="tile tile--navy">
                <span className="pill">Everything</span>
                <h3>Shop all {PRODUCT_COUNT} styles</h3>
                <p>Tees to fleece, and every style comes in sizes XS through XXL.</p>
                <span className="tile__cta" aria-hidden="true">
                  See products →
                </span>
              </Link>
            </li>
          </ul>
        </div>
      </section>

      <section className="section section--tinted">
        <div className="container split">
          <div className="split__media">
            <Seal className="seal--navy" />
          </div>
          <div className="split__copy">
            <p className="eyebrow">Our story</p>
            <h2>A family shop with a long memory</h2>
            <p>
              We opened our doors across from Yale in {FOUNDED}, and we've never moved. The next generation of
              the family runs the shop now, and the rules haven't changed: treat every customer like a regular,
              do honest work, and stand behind everything we sell.
            </p>
            <p>
              Next door, our own print and embroidery shop turns out team gear, event merchandise, and custom
              orders fast.
            </p>
            <Link to="/about" className="button button--primary">
              Read our story
            </Link>
          </div>
        </div>
      </section>

      <section className="cta-band">
        <div className="container cta-band__inner">
          <div>
            <h2>Make it official.</h2>
            <p>Create a free account and be the first to hear about new styles.</p>
          </div>
          <Link to="/create-account" className="button button--light">
            Create account
          </Link>
        </div>
      </section>
    </>
  )
}
