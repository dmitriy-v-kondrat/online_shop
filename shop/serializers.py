""" app.shop serializers. """

from rest_framework import serializers

from shop.models import ImagesProduct, Product


class ImagesSerializer(serializers.ModelSerializer):
    """ Serializer ImagesProduct model. """
    class Meta:
        model = ImagesProduct
        fields = ('image',)


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer product for listview. """
    detail = serializers.HyperlinkedIdentityField(view_name='detail_product', lookup_field='slug', read_only=True)
    images = serializers.SerializerMethodField()
    category = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = Product
        fields = ('detail', 'brand', 'name',
                  'price', 'discount', 'new_price',
                  'in_stock', 'quantity', 'category', 'images',
                  )

    def to_representation(self, obj):
        """ Remove or add fields. """
        rep = super().to_representation(obj)
        if obj.new_price is None:
            rep.pop('new_price')
            rep.pop('discount')
        else:
            rep['old_price'] = rep['price']
            rep.pop('price')
        return rep

    def get_images(self, obj):
        """ Show only one image. """
        request = self.context.get('request')
        if obj.images.all().exists():
            images = obj.images.first().image
            return request.build_absolute_uri(images.url)


class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer for Product detail view. """
    images = ImagesSerializer(many=True, read_only=True)
    category = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = Product
        fields = '__all__'

    def to_representation(self, obj):
        """ Remove or add fields. """
        rep = super().to_representation(obj)
        if obj.new_price is None:
            rep.pop('new_price')
            rep.pop('discount')
        else:
            rep['old_price'] = rep['price']
            rep.pop('price')
        return rep
