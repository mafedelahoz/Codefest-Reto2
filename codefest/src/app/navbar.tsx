"use client";
import Image from 'next/image'
import Link from 'next/link'


export default function Navbar() {
  return (
    <nav className="shadow  bg-sky-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link href="/subir_archivo" className="flex-shrink-0 flex items-center">
                <Image
                  className="h-8 w-auto"
                  src="/logoColombia.png"
                  alt="Logo"
                  width={32}
                  height={32}
                />
            </Link>
          </div>
        </div>
      </div>
    </nav>
  )
}