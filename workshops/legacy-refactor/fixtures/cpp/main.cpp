// Uses the legacy interface through three different paths. Only one of them is
// visible to a text search.

#include "legacy_api.h"

void Geometry::setLegacy(int value) { m_value = value; }
void Geometry::setModern(int value) { m_value = value; }

struct Source
{
    int value() const { return 7; }
};

int main()
{
    Geometry g;

    // Path 1: a direct call. A text search finds this one.
    g.setLegacy(1);

    // Path 2: three macro-generated accessors. A text search for "setLegacy"
    // finds nothing here. The names SetWidth, SetHeight and SetDepth do not
    // appear in any source file either, because the macro writes them.
    g.SetWidth(2);
    g.SetHeight(3);
    g.SetDepth(4);

    // Path 3: a template instantiation. The call inside setFrom is only
    // type-checked because this line instantiates it.
    Source s;
    g.setFrom(s);

    return 0;
}
