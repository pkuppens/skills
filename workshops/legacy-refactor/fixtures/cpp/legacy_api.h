// Minimal reproduction of the C++ case a text search cannot solve.
//
// This is a FIXTURE, not a real code base. It is small on purpose, so that the
// mechanism is visible in one screen. DCMTK and VTK show the same thing at a
// scale nobody can read.
//
// The point: SetWidth, SetHeight and SetDepth are never written anywhere. A
// macro writes them. Each one calls the deprecated setLegacy. A text search for
// "setLegacy" finds ONE line - the macro body. The compiler finds one call site
// per macro use.

#ifndef LEGACY_API_H
#define LEGACY_API_H

// gcc 4.9 predates the C++14 [[deprecated]] attribute, so a code base of this
// age uses the GNU attribute. Same effect, different spelling.
#define LEGACY_DEPRECATED __attribute__((deprecated("use setModern instead")))

class Geometry
{
public:
    // The old interface. One declaration, many callers.
    void setLegacy(int value) LEGACY_DEPRECATED;

    // The replacement.
    void setModern(int value);

// This macro generates an accessor. The generated name never appears in the
// source, which is exactly why a text search cannot count the call sites.
#define DECLARE_LEGACY_SETTER(Name) \
    void Set##Name(int v) { setLegacy(v); }

    DECLARE_LEGACY_SETTER(Width)
    DECLARE_LEGACY_SETTER(Height)
    DECLARE_LEGACY_SETTER(Depth)

    // A template adds a second invisible path: the body is only checked where
    // the template is instantiated.
    template <class T>
    void setFrom(const T& source) { setLegacy(source.value()); }

private:
    int m_value;
};

#endif // LEGACY_API_H
