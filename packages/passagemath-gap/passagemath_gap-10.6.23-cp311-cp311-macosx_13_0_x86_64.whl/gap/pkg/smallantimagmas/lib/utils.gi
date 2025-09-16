InstallGlobalFunction(AntimagmaGeneratorPossibleDiagonals,
    function(n)
        return Filtered(Tuples([1 .. n], n), t -> ForAll([1 .. n], i -> t[i] <> i));
end);

InstallGlobalFunction(AntimagmaGeneratorFilterNonIsomorphicMagmas,
    function(magmas)
        local result, m;
        result := [];

        while not IsEmpty(magmas) do
            m := First(magmas);
            Add(result, m);
            magmas := Filtered(magmas, n -> IsMagmaIsomorphic(m, n) = false);
        od;
        return result;
end);